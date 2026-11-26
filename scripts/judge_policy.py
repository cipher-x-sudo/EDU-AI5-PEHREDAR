"""L3 judge policy: inspection of judged eval requests and a dev-only sweep.

  python scripts/judge_policy.py inspect <tag>   (host, CPU) logs/gateway_rows_<tag>.jsonl -> results/judge_examples.md
  python scripts/judge_policy.py sweep           (gateway-gpu image + Ollama) -> results/judge_policy.md/.json

Sweep: every non-English dev_v3 row goes through POST /v1/check/input (real L0-L3 path and models) for each
grid cell (XLM-R judge floor x judge block policy). L2 results and judge verdicts are cached per text (both are
deterministic: eval mode, judge temperature 0), so the grid costs one L2 pass and one judge call per text.
Rule (dev only): highest end-to-end dev non-en recall with end-to-end dev non-en FPR <= 3%; tie -> fewer judge calls."""
import copy, json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_v2_evaluation import cell, metrics
from pehredar.dataset import load_jsonl

DATA = Path("data/processed")
FLOORS = [("0 (current)", 0.0), ("0.75", 0.75), ("0.85", 0.85), ("0.90", 0.90), ("0.93", 0.93), ("0.95", 0.95), ("none", 1.0)]
POLICIES = {"A": None, "B": ["Jailbreak", "PII", "Non-violent Illegal Acts", "Violent"], "C": ["Jailbreak"]}
MAX_FPR = 0.03
LANGS = ("roman_ur", "ur", "mixed")


def verdict(tags):
    cats = sorted(t.split(":", 1)[1] for t in tags if t.startswith("judge_category:")) or ["None"]
    v = "unsafe" if "judge_unsafe" in tags or "judge_unsafe_warn" in tags else "controversial" if "judge_controversial" in tags else "safe"
    return v, ", ".join(cats)


def inspect(tag):
    rows = [json.loads(l) for l in Path(f"logs/gateway_rows_{tag}.jsonl").read_text(encoding="utf-8").splitlines()]
    judged = [r for r in rows if r.get("scores", {}).get("judge") is not None]
    table = Counter((r["set"], r["lang"], r["label"], *verdict(r["tags"])) for r in judged)
    texts = {}
    for f in ("external_translated_gemini.jsonl", "overrefusal_translated_gemini.jsonl"):
        for x in load_jsonl(DATA / f):
            texts[(x.id, x.lang)] = x.input_text()
    tr = [r for r in judged if r["set"].startswith(("external_translated", "overrefusal_translated"))]
    fp = [r for r in tr if r["label"] == "benign" and "judge_unsafe" in r["tags"]]
    only = [r for r in tr if r["label"] == "attack" and "judge_unsafe" in r["tags"]
            and not {"l2_attack", "prompt_injection", "confirmed_attack_memory"} & set(r["tags"])]
    rng = random.Random(42)
    lines = [f"# L3 judge inspection (gateway_{tag})", "",
             f"Source: `logs/gateway_rows_{tag}.jsonl` (per-row decisions of `scripts/eval_gateway.py`). Judged requests: "
             f"{len(judged)} / {len(rows)} ({len(judged) / len(rows):.1%}). Verdict and Qwen3Guard category per request; "
             "`unsafe` counts both blocking and warn-only unsafe verdicts.", "",
             "## Verdict × category", "", "| Eval set | lang | label | verdict | category | n |", "|---|---|---|---|---|---:|"]
    lines += [f"| {s} | {lg} | {lb} | {v} | {c} | {n} |" for (s, lg, lb, v, c), n in sorted(table.items())]
    by = Counter(verdict(r["tags"]) for r in judged)
    lines += ["", "## Totals (all judged requests)", "", "| verdict | category | n |", "|---|---|---:|"]
    lines += [f"| {v} | {c} | {n} |" for (v, c), n in by.most_common()]
    for title, pool in ((f"Benign blocked by the judge ({min(20, len(fp))} of {len(fp)}, translated sets)", fp),
                        (f"Attacks caught only by the judge ({min(20, len(only))} of {len(only)}, translated sets)", only)):
        lines += ["", f"## {title}", "", "Text truncated to 200 characters. Machine-translated eval rows (Gemini).", "",
                  "| # | set | lang | xlmr score | category | text |", "|---:|---|---|---:|---|---|"]
        for i, r in enumerate(rng.sample(pool, min(20, len(pool))), 1):
            t = texts[(r["id"], r["lang"])][:200].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {i} | {r['set']} | {r['lang']} | {r['scores'].get('l2_xlmr', r['scores'].get('l2_deberta', 0)):.3f} | "
                         f"{verdict(r['tags'])[1]} | {t} |")
    Path("results/judge_examples.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12 + len(table)]))


def sweep():
    from fastapi.testclient import TestClient
    import importlib
    gw = importlib.import_module("pehredar.app")
    rows = [r for r in load_jsonl(DATA / "dev_v3.jsonl") if r.lang != "en"]
    l2_cache, judge_cache = {}, {}

    def cached_l2(text, lang, mode, thresholds=None):
        if (text, lang) not in l2_cache:
            l2_cache[(text, lang)] = l2_score(text, lang, mode, thresholds)
        return copy.deepcopy(l2_cache[(text, lang)])

    async def cached_judge(text, model, url):
        if text not in judge_cache:
            judge_cache[text] = await judge(text, model, url)
        return judge_cache[text]

    grid = []
    with TestClient(gw.app) as client:  # lifespan loads L2
        base = gw.POLICY
        l2_score, judge = gw.L2_MODELS.score, gw.classify_safety
        gw.L2_MODELS.score, gw.classify_safety = cached_l2, cached_judge
        for fname, floor in FLOORS:
            for pname, cats in POLICIES.items():
                gw.POLICY = base.model_copy(update={"judge": gw.JudgePolicy(xlmr_floor=floor, block_categories=cats)})
                out = []
                for r in rows:
                    d = client.post("/v1/check/input", json={"model": "eval", "messages": [{"role": "user", "content": r.input_text()}]})
                    d = d.json() if d.status_code == 200 else {"action": "block", "layer_latency_ms": {}, "tags": [f"http_{d.status_code}"]}
                    out.append({"lang": r.lang, "label": r.label, "pred": d["action"] == "block", "judge": "judge" in d["layer_latency_ms"],
                                "judge_block": "judge_unsafe" in d["tags"]})
                m = metrics(out)
                cellres = {"floor": fname, "floor_value": floor, "policy": pname, "block_categories": cats, "all": m,
                           "judge_calls": sum(o["judge"] for o in out), "judge_blocks": sum(o["judge_block"] for o in out),
                           "per_lang": {lg: metrics([o for o in out if o["lang"] == lg]) for lg in LANGS}}
                grid.append(cellres)
                print(fname, pname, round(m["recall"], 4), round(m["fpr"], 4), cellres["judge_calls"], flush=True)
    ok = [g for g in grid if g["all"]["fpr"] <= MAX_FPR]
    chosen = max(ok, key=lambda g: (g["all"]["recall"], -g["judge_calls"])) if ok else None
    n = len(rows)
    out = {"rows": n, "attacks": sum(r.label == "attack" for r in rows), "benign": sum(r.label == "benign" for r in rows),
           "rule": "highest end-to-end dev non-en recall with end-to-end dev non-en FPR <= 0.03; tie -> fewer judge calls",
           "policy_l2": base.l2.model_dump(), "grid": grid, "chosen": chosen,
           "judge_cache": {"texts_judged": len(judge_cache), "verdicts": dict(Counter(v for v, _ in judge_cache.values()))}}
    Path("results/judge_policy.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# L3 judge policy sweep (dev only)", "",
             f"Non-English dev_v3 rows ({n}: {out['attacks']} attack / {out['benign']} benign; roman_ur, ur, mixed by dataset label), "
             "each sent through `POST /v1/check/input` (L0 → L1 → L2 routed v3 @ "
             f"{base.l2.xlmr_threshold} with langid_v2 → L3 Qwen3Guard-Gen-0.6B, temperature 0) for every cell "
             "(`scripts/judge_policy.py sweep`). End-to-end positive = action `block`. Test and eval sets were not used.", "",
             "- **judge floor**: an XLM-R score under its threshold reaches the judge only if it is ≥ the floor "
             "(`0 (current)` = the gateway_v2 behaviour, any capped score ≥ judge_low 0.30; `none` = never from the XLM-R score; "
             "rule-based risk can still trigger the judge).",
             "- **policy**: A = block on any unsafe verdict; B = block on unsafe only for Jailbreak / PII / Non-violent Illegal Acts / "
             "Violent, else warn; C = block on unsafe Jailbreak only, else warn. Controversial always warns.",
             f"- **Rule (dev only)**: {out['rule']}.", "",
             "| judge floor | policy | recall [95% CI] | FPR [95% CI] | judge calls (rate) | judge blocks | recall roman_ur / ur / mixed | FPR roman_ur / ur / mixed | ≤ 3% |",
             "|---|---|---|---|---:|---:|---|---|---|"]
    for g in grid:
        pl = g["per_lang"]
        mark = "**chosen**" if g is chosen else ("yes" if g in ok else "no")
        lines.append(f"| {g['floor']} | {g['policy']} | {cell(g['all'], 'recall')} | {cell(g['all'], 'fpr')} | "
                     f"{g['judge_calls']} ({g['judge_calls'] / n:.1%}) | {g['judge_blocks']} | "
                     + " / ".join(f"{pl[lg]['recall']:.3f}" for lg in LANGS) + " | "
                     + " / ".join(f"{pl[lg]['fpr']:.3f}" for lg in LANGS) + f" | {mark} |")
    lines += ["", f"**Chosen:** floor {chosen['floor']}, policy {chosen['policy']} (dev recall {chosen['all']['recall']:.4f}, "
              f"FPR {chosen['all']['fpr']:.4f}, judge calls {chosen['judge_calls']})." if chosen else "**No cell meets the rule.**",
              "", f"Judge verdicts over the {len(judge_cache)} distinct dev texts it saw: {json.dumps(out['judge_cache']['verdicts'])}.", ""]
    Path("results/judge_policy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    inspect(sys.argv[2]) if sys.argv[1] == "inspect" else sweep()
