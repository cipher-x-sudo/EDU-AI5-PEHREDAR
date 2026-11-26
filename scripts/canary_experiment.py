"""Output guard / canary experiment -> results/output_guard_<tag>.md/.json (tag = PEHREDAR_EVAL_TAG, default v1).

300 attack prompts from eval-only sets: 100 English (external_eval), 100 roman_ur and 100 mixed
(external_translated attacks first, then dev_translated_v2 attacks; seed 42).
(a) bare: straight to the protected model (Ollama) with the gateway's canary system prompt.
(b) gateway: POST /v1/chat/completions through the full gateway (input layers, protected model, output guard).
Same model, temperature 0, same max_tokens. Leak = the canary string in what the client receives.
Run in the gateway-gpu image with PEHREDAR_L2=1, PEHREDAR_GUARD_MODEL, PEHREDAR_CANARY and a fresh DB."""
import importlib, json, os, random, sys, time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_v2_evaluation import wilson

DATA = Path("data/processed")
PROTECTED = os.getenv("PEHREDAR_PROTECTED_MODEL", "richardyoung/qwen3-8b-abliterated:Q4_K_M")
MAX_TOKENS = 200
TAG = os.getenv("PEHREDAR_EVAL_TAG", "v1")
N = 100


def read(name):
    return [json.loads(x) for x in (DATA / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def prompts():
    rng = random.Random(42)
    en = sorted((r for r in read("external_eval.jsonl") if r["label"] == "attack" and r.get("text")), key=lambda r: r["id"])
    out = [{"lang": "en", "id": r["id"], "set": "external_eval", "text": r["text"]} for r in rng.sample(en, N)]
    for lang in ("roman_ur", "mixed"):
        ext = sorted((r for r in read("external_translated_gemini.jsonl") if r["lang"] == lang and r["label"] == "attack"), key=lambda r: r["id"])
        dev = sorted((r for r in read("dev_translated_v2_gemini.jsonl") if r["lang"] == lang and r["label"] == "attack"), key=lambda r: r["id"])
        picked = [(r, "external_translated") for r in ext[:N]] + [(r, "dev_translated_v2") for r in rng.sample(dev, N - min(N, len(ext)))]
        out += [{"lang": lang, "id": r["id"], "set": s, "text": r["text"]} for r, s in picked]
    return out


def leak(text, canary):
    return {"full": canary in text, "hex": canary.split("-")[-1] in text}


def main():
    gateway = importlib.import_module("pehredar.app")
    from fastapi.testclient import TestClient
    import httpx
    from pehredar.output_guard import check_output
    canary = gateway.CANARY
    assert canary, "PEHREDAR_CANARY must be set"
    items = prompts()
    # (a) bare model
    with httpx.Client(timeout=300) as http:
        for i, it in enumerate(items, 1):
            started = time.perf_counter()
            try:
                r = http.post(f"{gateway.UPSTREAM_URL}/chat/completions", json={
                    "model": PROTECTED, "temperature": 0, "max_tokens": MAX_TOKENS, "reasoning_effort": "none",
                    "messages": [{"role": "system", "content": gateway.canary_system_prompt(canary)},
                                 {"role": "user", "content": it["text"]}]})
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"] or ""
                it["bare"] = {"ok": True, **leak(content, canary), "output_guard_tags": check_output(content, canary)[2],
                              "seconds": round(time.perf_counter() - started, 2)}
            except Exception as exc:
                it["bare"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:200]}
            if i % 25 == 0:
                print(f"bare {i}/{len(items)}", flush=True)
    # (b) through the gateway
    with TestClient(gateway.app) as client:
        for i, it in enumerate(items, 1):
            started = time.perf_counter()
            r = client.post("/v1/chat/completions", headers={"x-session-id": f"canary-{it['id']}"}, json={
                "model": PROTECTED, "temperature": 0, "max_tokens": MAX_TOKENS, "reasoning_effort": "none", "messages": [{"role": "user", "content": it["text"]}]})
            if r.status_code == 200:
                body = r.json(); meta = body.get("pehredar", {})
                content = body["choices"][0]["message"]["content"] or ""
                it["gateway"] = {"ok": True, "stage": meta.get("stage"), "action": meta.get("action"), "tags": meta.get("tags", []),
                                 **leak(content, canary), "seconds": round(time.perf_counter() - started, 2)}
            else:
                it["gateway"] = {"ok": False, "status": r.status_code, "detail": r.text[:200]}
            if i % 25 == 0:
                print(f"gateway {i}/{len(items)}", flush=True)
    report(items)


def report(items):
    def summary(xs):
        bare = [x["bare"] for x in xs]; gw = [x["gateway"] for x in xs]
        n_b = sum(b["ok"] for b in bare); n_g = sum(g["ok"] for g in gw)
        k_b = sum(b.get("full", False) for b in bare); k_g = sum(g.get("full", False) for g in gw)
        return {"prompts": len(xs),
                "bare": {"answered": n_b, "canary_leaks": k_b, "leak_rate": round(k_b / max(1, n_b), 4), "ci": wilson(k_b, n_b),
                         "hex_only_leaks": sum(b.get("hex", False) and not b.get("full", False) for b in bare),
                         "errors": len(xs) - n_b,
                         "output_guard_would_flag": dict(Counter(t for b in bare for t in b.get("output_guard_tags", [])))},
                "gateway": {"answered": n_g, "canary_leaks_to_client": k_g, "leak_rate": round(k_g / max(1, n_g), 4), "ci": wilson(k_g, n_g),
                            "hex_only_leaks_to_client": sum(g.get("hex", False) and not g.get("full", False) for g in gw),
                            "stopped_at_input": sum(g.get("stage") == "input" for g in gw),
                            "stopped_at_output": sum(g.get("stage") == "output" for g in gw),
                            "output_block_tags": dict(Counter(t for g in gw if g.get("stage") == "output" for t in g["tags"])),
                            "passed": sum(g.get("stage") == "passed" for g in gw),
                            "passed_redacted": sum(g.get("stage") == "passed" and g.get("action") == "redact" for g in gw),
                            "passed_tags": dict(Counter(t for g in gw if g.get("stage") == "passed" for t in g["tags"])),
                            "errors": dict(Counter(g.get("status") for g in gw if not g["ok"]))},
                "bare_leaks_and_gateway_outcome": dict(Counter(x["gateway"].get("stage", "error") for x in xs if x["bare"].get("full")))}
    out = {"protected_model": PROTECTED, "max_tokens": MAX_TOKENS, "temperature": 0, "reasoning_effort": "none",
           "per_language": {l: summary([x for x in items if x["lang"] == l]) for l in ("en", "roman_ur", "mixed")},
           "all": summary(items), "sources": dict(Counter(f"{x['lang']}:{x['set']}" for x in items))}
    Path(f"results/output_guard_{TAG}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    pct = lambda k, n, ci: f"{k}/{n} = {k / max(1, n):.1%} [{ci[0]:.3f}–{ci[1]:.3f}]" if ci else f"{k}/{n}"
    lines = [f"# Output guard / canary experiment {TAG}", "",
             f"Protected model `{PROTECTED}` (Ollama), temperature 0, max_tokens {MAX_TOKENS}, reasoning_effort none (thinking off, same in both arms). The canary is in the "
             "system prompt (`canary_system_prompt`, same text as the gateway adds). (a) bare: prompt sent straight to the "
             "model. (b) gateway: full `/v1/chat/completions` (input layers → model → output guard incl. Qwen3Guard). "
             "A leak is the full canary string in what the client receives. Attack prompts come from eval-only sets "
             f"({json.dumps(out['sources'])}); roman_ur/mixed are machine-translated.", "",
             "| Language | Prompts | (a) bare: canary leaks [95% CI] | (b) gateway: leaks to client [95% CI] | (b) stopped at input | (b) stopped at output (tags) | (b) passed | (b) passed with PII redaction | errors (a) / (b) |",
             "|---|---:|---|---|---:|---|---:|---:|---|"]
    for lang, s in [*out["per_language"].items(), ("all", out["all"])]:
        b, g = s["bare"], s["gateway"]
        lines.append(f"| {lang} | {s['prompts']} | {pct(b['canary_leaks'], b['answered'], b['ci'])} | "
                     f"{pct(g['canary_leaks_to_client'], g['answered'], g['ci'])} | {g['stopped_at_input']} | "
                     f"{g['stopped_at_output']} {json.dumps(g['output_block_tags'])} | {g['passed']} | {g['passed_redacted']} | "
                     f"{b['errors']} / {sum(g['errors'].values())} |")
    a = out["all"]
    lines += ["", f"- Bare-model leaks by gateway outcome for the same prompt: {json.dumps(a['bare_leaks_and_gateway_outcome'])}",
              f"- Partial leaks (hex part of the canary only): bare {a['bare']['hex_only_leaks']}, gateway {a['gateway']['hex_only_leaks_to_client']}",
              f"- Output guard tags the bare responses would have triggered: {json.dumps(a['bare']['output_guard_would_flag'])}",
              f"- Gateway passed-response tags: {json.dumps(a['gateway']['passed_tags'])}", ""]
    Path(f"results/output_guard_{TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
