job: translation-pilot
state: done
result: 91/200 effective passed (45.5%)
failures: script/length/PII plus JSON parse errors
ollama: stopped


job: download-new-data
state: done
pid: 36092
started: 2026-11-24T19:58:47.5525437+05:00

job: unify-v1b
state: done
pid: 25976
started: 2026-11-24T20:06:55.4040453+05:00

job: translation-retry
state: stopped
pid: 36908
started: 2026-11-24T20:13:19.7106764+05:00

job: embedding-audit-v1b
state: stopped-before-run
reason: serialized behind translation pilot

job: v1b-train
state: done
result: one epoch completed on CUDA; peak VRAM 5.24 GB

job: tests
state: done
result: 52 passed

job: v1-evaluation
state: stopped
result: ProtectAI DeBERTa pass over expanded data exceeded runtime; no accuracy claim

job: translation-retry
state: stopped
result: 26/50 at stop; script/JSON failures persisted; prior completed 200-row pilot 91/200 (45.5%)
ollama: stopped

job: v1b-smoke
state: running
pid: 29932
started: 2026-11-24T20:26:57.3773323+05:00

job: v1b-train
state: running
pid: 6504
started: 2026-11-24T20:35:13.0043760+05:00
model: models/clf_v1b
epochs: 1

job: v1-evaluation
state: stopped
reason: CPU DeBERTa evaluation exceeded practical runtime after dataset expansion; no complete v1 report generated

job: embedding-audit-v1b
state: running
pid: 33148
started: 2026-11-24T22:10:38.9682323+05:00
output: data/processed/dev_public_v1b.jsonl

job: cached-v1b-evaluation
state: running
pid: 38772
started: 2026-11-24T22:22:56.6726753+05:00
cache: results/cache

job: translation-quality-50
state: running
pid: 31952
started: 2026-11-24T22:42:54.5868152+05:00
models: qwen3:8b -> abliterated fallback

job: translation-quality-50
state: done
result: 100/150 outputs passed (66.7%); fallback abliterated produced accepted samples; Ollama stopped

job: cached-v1b-evaluation
state: done
result: results/clf_v1.md and results/v1_evaluation.json refreshed; container exited 0; cache reused

job: embedding-audit-v1b
state: done
result: 585 embedding candidate pairs; 588 dev rows; 1114 whole split_groups removed; dev_public_v1b=5645; train unchanged

job: translation-quality-50
state: done
result: 50 rows / 150 outputs; 100 passed, 50 failed (66.7%); primary qwen3:8b with abliterated fallback; Ollama stopped

job: docker-tests
state: done
result: 52 passed, 1 warning; derived dev_public_v1b excluded from global ID uniqueness check because it intentionally duplicates source rows

BIPIA: test-only locally; benchmark/code/test.jsonl=50, benchmark/email/test.jsonl=50, benchmark/table/test.jsonl=100; no train split found

job: v1-evaluation-fixed
state: done
result: saved thresholds per model, dev_public_v1b, shared 512 head+tail encoder; v0 sanity 0.6142 (old 0.5939 was 256-token path)
tests: 53 passed
job: unify-v2
state: running
started: 2026-11-24T23:36:48+05:00

job: ensemble-eval-v1
state: running
log: logs/ensemble_eval_v1.log
started: 2026-11-24T23:58:44+05:00

job: translation-v2
state: running (detached container pehredar-translation-v2)
log: logs/translation_v2.log
started: 2026-11-25T00:25:35+05:00
plan: 2,500 attack + 2,500 benign train rows x 3 langs; Ollama stops when done
translation-v2 2026-11-25T00:28:27+05:00: restarted as two-stage run (qwen3:8b pass, then abliterated on rejects)
translation-v2 2026-11-25T00:56:50+05:00: progress stage1 2500/14997 sec_per_output=0.65 eta_h=2.3
translation-v2 2026-11-25T00:58:29+05:00: progress stage1 2500/14997 sec_per_output=0.65 eta_h=2.3
translation-v2 2026-11-25T01:26:50+05:00: progress stage1 3000/14997 sec_per_output=1.12 eta_h=3.7
translation-v2 2026-11-25T01:28:29+05:00: progress stage1 3000/14997 sec_per_output=1.12 eta_h=3.7

job: unify-v2 / split-v2 / embedding-audit-v2 / near-dup-repair-v2
state: done
result: pool 44,700 (17,880 attack / 26,820 benign); train_public_v2 40,229; dev_public_v2 3,976; check_split passes

job: ensemble-eval-v1
state: done
result: results/ensemble_v1.md
