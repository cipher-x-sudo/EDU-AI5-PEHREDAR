"""Freeze the evaluated gateway configuration -> results/final_config.md / .json (host; reads files only).

Records model dirs with SHA-256 per file, thresholds, router, judge policy, policy.yaml hash, compose env and the
commit. Run after the config commit, before tagging. Does not touch data/frozen_test or data/private_*."""
import hashlib, json, re, subprocess
from pathlib import Path

import yaml

FILES = {"xlmr (non-English L2)": Path("models/clf_v3_e3"), "langid_v2 (router)": Path("models/langid_v2.joblib"),
         "deberta (English L2)": next(Path("models/hf_cache/hub").glob("models--protectai--deberta-v3-base-prompt-injection-v2/snapshots/*"), None)}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def main():
    policy_path = Path("config/policy.yaml")
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    compose = yaml.safe_load(Path("compose.yaml").read_text(encoding="utf-8"))["services"]["gateway-gpu"]["environment"]
    report = json.loads((FILES["xlmr (non-English L2)"] / "training_report.json").read_text(encoding="utf-8"))
    models = {}
    for name, path in FILES.items():
        files = sorted(p for p in (path.rglob("*") if path.is_dir() else [path]) if p.is_file())
        models[name] = {"path": str(path).replace("\\", "/"), "files": {str(p.relative_to(path) if path.is_dir() else p.name).replace("\\", "/"): sha(p) for p in files}}
    try:
        ollama = subprocess.run(["docker", "exec", "pehredar-ollama-1", "ollama", "list"], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        ollama = ""
    ids = {m.group(1): m.group(2) for m in re.finditer(r"^(\S+)\s+([0-9a-f]{12})\s", ollama, re.M)}
    guard = compose["PEHREDAR_GUARD_MODEL"]
    out = {"commit": git("rev-parse", "HEAD"), "commit_subject": git("log", "-1", "--format=%s"),
           "policy_yaml_sha256": sha(policy_path), "policy": policy, "gateway_gpu_env": compose, "models": models,
           "xlmr_training_report": report, "guard_model": {"name": guard, "ollama_id": ids.get(guard)},
           "protected_model_in_experiments": {"name": "richardyoung/qwen3-8b-abliterated:Q4_K_M",
                                              "ollama_id": ids.get("richardyoung/qwen3-8b-abliterated:Q4_K_M")}}
    Path("results/final_config.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    j, l2, t = policy.get("judge", {}), policy["l2"], policy["thresholds"]
    lines = ["# Final evaluated gateway configuration (v1.0-eval-config)", "",
             f"- Commit: `{out['commit']}` ({out['commit_subject']}); git tag `v1.0-eval-config`.",
             f"- `config/policy.yaml` SHA-256: `{out['policy_yaml_sha256']}`.",
             "- Frozen human test set: **not evaluated** (`scripts/eval_frozen.py` is run once by the team after the human test set exists).", "",
             "## Pipeline", "",
             "| Layer | Setting |", "|---|---|",
             "| L0 | `pehredar/normalizer.py` |",
             "| L1 | rules (`pehredar/rules.py`) + confirmed-attack memory |",
             f"| Router | langid_v2 (`{compose['PEHREDAR_LANGID_MODEL']}`): char 1–5 TF-IDF + LR, Roman-Urdu override, low confidence < 0.6 → mixed |",
             f"| L2 en | ProtectAI DeBERTa v3 base prompt-injection v2, threshold 0.5 |",
             f"| L2 non-en | XLM-R base v3 (`{compose['PEHREDAR_L2_XLMR_DIR']}`, encoder v2 512 head+tail), threshold {l2['xlmr_threshold']} "
             f"(2.75% L2-only dev non-en FPR, chosen jointly with the judge in results/judge_policy_joint.md); the model's own 2% all-dev threshold is {report.get('threshold'):.4f} |",
             f"| L2 mode | {l2['mode']} |",
             f"| Gateway thresholds | warn {t['warn']}, judge_low {t['judge_low']}, block {t['block']}; L2 scores under their threshold are capped below block |",
             f"| L3 judge | `{guard}` (temperature 0); XLM-R judge floor {j.get('xlmr_floor', 0.0)}; blocks on unsafe categories "
             f"{j.get('block_categories') or 'any'}; controversial / other unsafe → warn (results/judge_policy_joint.md) |",
             "| Output guard | canary + PII redaction + Qwen3Guard on the response |", "",
             "## Model files (SHA-256)", ""]
    for name, m in models.items():
        lines += [f"**{name}** — `{m['path']}`", "", "| file | sha256 |", "|---|---|"]
        lines += [f"| {f} | `{h}` |" for f, h in m["files"].items()] + [""]
    lines += [f"Ollama IDs: guard {out['guard_model']['ollama_id'] or 'n/a (Ollama not running)'}; protected model (experiments only) "
              f"{out['protected_model_in_experiments']['ollama_id'] or 'n/a'}.", "",
              "Weights are not in git. XLM-R v3: `scripts/train_classifier.py`, run recorded in `models/clf_v3_e3/model_card.md` (data commit, dataset SHA-256, seed 42) on `data/processed/train_v3.jsonl`; langid_v2: "
              "`python -m scripts.train_langid`; DeBERTa from the Hugging Face snapshot above.", ""]
    Path("results/final_config.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main()
