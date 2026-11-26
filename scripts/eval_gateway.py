"""End-to-end gateway evaluation -> results/gateway_<tag>.md/.json (tag = PEHREDAR_EVAL_TAG, default v1).

Runs every row through POST /v1/check/input (L0 normalizer, L1 rules + memory, L2 routed ensemble,
session escalation, L3 Qwen3Guard judge for uncertain cases) in-process with the real models.
Full gateway: positive = action "block" (413 = refused, counted as block).
L2 only: positive = the routed L2 model over its threshold (tag l2_attack) on the same request.
Run in the gateway-gpu image with PEHREDAR_L2=1, PEHREDAR_GUARD_MODEL and a fresh PEHREDAR_DB_PATH."""
import json, os, statistics, subprocess, sys, time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_v2_evaluation import cell, metrics
from pehredar.dataset import load_jsonl

DATA = Path("data/processed")
SETS = [("external_eval", "external_eval.jsonl", None, None), ("injecagent (unseen)", "indirect_eval.jsonl", "injecagent", None),
        ("bipia (unseen)", "indirect_eval.jsonl", "bipia", None), ("xstest FPR", "overrefusal_eval.jsonl", "xstest", None),
        ("or_bench FPR", "overrefusal_eval.jsonl", "or_bench", None), ("benign_email_probe FPR", "benign_email_probe.jsonl", None, None),
        ("external_translated roman_ur", "external_translated_gemini.jsonl", None, "roman_ur"),
        ("external_translated ur", "external_translated_gemini.jsonl", None, "ur"),
        ("external_translated mixed", "external_translated_gemini.jsonl", None, "mixed"),
        ("overrefusal_translated FPR roman_ur", "overrefusal_translated_gemini.jsonl", None, "roman_ur"),
        ("overrefusal_translated FPR ur", "overrefusal_translated_gemini.jsonl", None, "ur"),
        ("overrefusal_translated FPR mixed", "overrefusal_translated_gemini.jsonl", None, "mixed")]
TAG = os.getenv("PEHREDAR_EVAL_TAG", "v1")
# Layer credited with a block, in pipeline order (a block can carry several tags; the first match wins).
BLOCK_LAYERS = (("L1 rules", "prompt_injection"), ("L1 memory", "confirmed_attack_memory"), ("L2", "l2_attack"), ("L3 judge", "judge_unsafe"))


def blocked_by(r):
    if r["status"] != 200:
        return f"http_{r['status']}"
    return next((name for name, tag in BLOCK_LAYERS if tag in r["tags"]), "risk/escalation only")
LAYERS = ("normalization", "rules", "l2", "memory", "session", "judge")


def gpu_memory():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        used, total = (int(x) for x in out.split(","))
        return {"used_mib": used, "total_mib": total}
    except Exception as exc:
        return {"error": str(exc)}


def pct(xs, p):
    s = sorted(xs)
    return round(s[min(len(s) - 1, int(p * len(s)))], 2) if s else None


def main():
    from fastapi.testclient import TestClient
    import importlib
    gateway = importlib.import_module("pehredar.app")
    rows_out = []
    with TestClient(gateway.app) as client:
        l2_status = gateway.L2_MODELS.status() if gateway.L2_MODELS else None
        for label, filename, source, lang in SETS:
            for r in load_jsonl(DATA / filename):
                if (source and r.source != source) or (lang and r.lang != lang):
                    continue
                started = time.perf_counter()
                resp = client.post("/v1/check/input", json={"model": "eval", "messages": [{"role": "user", "content": r.input_text()}]})
                e2e = (time.perf_counter() - started) * 1000
                if resp.status_code == 200:
                    d = resp.json()
                    rows_out.append({"set": label, "label": r.label, "lang": r.lang, "detected": d["language"], "status": 200,
                                     "action": d["action"], "tags": d["tags"], "l2_hit": "l2_attack" in d["tags"],
                                     "judge": "judge" in d["layer_latency_ms"], "lat": d["layer_latency_ms"], "e2e": e2e})
                else:
                    rows_out.append({"set": label, "label": r.label, "lang": r.lang, "detected": None, "status": resp.status_code,
                                     "action": "block", "tags": [f"http_{resp.status_code}"], "l2_hit": False, "judge": False,
                                     "lat": {}, "e2e": e2e})
            print(label, sum(x["set"] == label for x in rows_out), flush=True)
        vram = {"after_run_all_models_loaded": gpu_memory(), "l2_torch_allocated_gb": l2_status and l2_status["vram_allocated_gb"]}
    report(rows_out, l2_status, vram, gateway.POLICY.l2.model_dump())


def report(rows, l2_status, vram, policy_l2=None):
    results = {}
    for label, *_ in SETS:
        rs = [r for r in rows if r["set"] == label]
        results[label] = {
            "gateway": metrics([{"label": r["label"], "pred": r["action"] == "block"} for r in rs]),
            "l2_only": metrics([{"label": r["label"], "pred": r["l2_hit"]} for r in rs]),
            "warn": sum(r["action"] == "warn" for r in rs), "judge_calls": sum(r["judge"] for r in rs),
            "judge_outcomes": dict(Counter(t for r in rs for t in r["tags"] if t.startswith("judge_"))),
            "http_errors": dict(Counter(r["status"] for r in rs if r["status"] != 200)),
            "rule_hits": sum("prompt_injection" in r["tags"] for r in rs),
            "blocks_by_layer": dict(Counter(blocked_by(r) for r in rs if r["action"] == "block")),
            "detected_lang": dict(Counter(r["detected"] for r in rs)), "fallback_tags": sum(any(t.startswith("l2_f") for t in r["tags"]) for r in rs)}
    ok = [r for r in rows if r["status"] == 200]
    latency = {layer: {"median_ms": pct([r["lat"][layer] for r in ok if layer in r["lat"]], .5),
                       "p95_ms": pct([r["lat"][layer] for r in ok if layer in r["lat"]], .95),
                       "n": sum(layer in r["lat"] for r in ok)} for layer in LAYERS}
    latency["end_to_end"] = {"median_ms": pct([r["e2e"] for r in ok], .5), "p95_ms": pct([r["e2e"] for r in ok], .95), "n": len(ok)}
    out = {"l2": l2_status, "vram": vram, "requests": len(rows), "judge_calls": sum(r["judge"] for r in rows),
           "results": results, "latency": latency,
           "policy_l2": policy_l2, "env": {k: os.getenv(k) for k in ("PEHREDAR_GUARD_MODEL", "PEHREDAR_L2_XLMR_DIR", "PEHREDAR_LANGID_MODEL")}}
    Path(f"results/gateway_{TAG}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = [f"# Gateway {TAG}: end-to-end evaluation", "",
             "Every row was sent to `POST /v1/check/input` (L0 normalizer → L1 rules + memory → L2 routed ensemble → session "
             "escalation → L3 Qwen3Guard judge when judge_low ≤ risk < block), in-process with the real models "
             "(`scripts/eval_gateway.py`). **Full gateway** counts action `block` (HTTP 413 refusals counted as block). "
             "**L2 only** counts the routed L2 model over its threshold on the same request. `warn` is not counted as a block. "
             "Language for routing comes from the shared detector (`pehredar/langid.py`), not from the dataset label. "
             "Translated sets are Gemini machine translations (not the human test set).", "",
             f"- Config: {json.dumps(out['env'])}; policy l2 = {json.dumps(out['policy_l2'])}",
             f"- L2: {json.dumps(l2_status)}", f"- GPU memory: {json.dumps(vram)}",
             f"- Requests: {len(rows)}; L3 judge calls: {out['judge_calls']} ({out['judge_calls'] / max(1, len(rows)):.1%})", "",
             "| Eval set | Full gateway recall [95% CI] | Full gateway FPR [95% CI] | L2-only recall [95% CI] | L2-only FPR [95% CI] | warn | L3 calls | L3 outcome | blocks by layer | detected language |",
             "|---|---|---|---|---|---:|---:|---|---|---|"]
    for label, x in results.items():
        g, l = x["gateway"], x["l2_only"]
        lines.append(f"| {label} | {cell(g, 'recall')} | {cell(g, 'fpr')} | {cell(l, 'recall')} | {cell(l, 'fpr')} | {x['warn']} | "
                     f"{x['judge_calls']} | {json.dumps(x['judge_outcomes'])} | {json.dumps(x['blocks_by_layer'])} | {json.dumps(x['detected_lang'])} |")
    lines += ["", "## Latency (ms)", "", "| Layer | median | p95 | requests that ran it |", "|---|---:|---:|---:|"]
    for layer, v in latency.items():
        lines.append(f"| {layer} | {v['median_ms']} | {v['p95_ms']} | {v['n']} |")
    lines += ["", "End-to-end = client-side time for one in-process `/v1/check/input` call (includes the judge when called "
              "and the decision log write). Judge latency is over judged requests only.", ""]
    Path(f"results/gateway_{TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
