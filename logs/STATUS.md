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
translation-v2 2026-11-25T01:56:51+05:00: progress stage1 3600/14997 sec_per_output=1.45 eta_h=4.6
translation-v2 2026-11-25T01:58:29+05:00: progress stage1 3600/14997 sec_per_output=1.45 eta_h=4.6
translation-v2 2026-11-25T02:26:51+05:00: progress stage1 4200/14997 sec_per_output=1.64 eta_h=4.9
translation-v2 2026-11-25T02:28:30+05:00: progress stage1 4300/14997 sec_per_output=1.66 eta_h=4.9
translation-v2 2026-11-25T02:56:52+05:00: progress stage1 4900/14997 sec_per_output=1.78 eta_h=5.0
translation-v2 2026-11-25T02:58:30+05:00: progress stage1 5000/14997 sec_per_output=1.79 eta_h=5.0
translation-v2 2026-11-25T03:26:52+05:00: progress stage1 5600/14997 sec_per_output=1.88 eta_h=4.9
translation-v2 2026-11-25T03:28:30+05:00: progress stage1 5600/14997 sec_per_output=1.88 eta_h=4.9
translation-v2 2026-11-25T03:56:53+05:00: progress stage1 6000/14997 sec_per_output=2.04 eta_h=5.1
translation-v2 2026-11-25T03:58:31+05:00: progress stage1 6000/14997 sec_per_output=2.04 eta_h=5.1
translation-v2 2026-11-25T04:26:53+05:00: progress stage1 6400/14997 sec_per_output=2.21 eta_h=5.3
translation-v2 2026-11-25T04:28:31+05:00: progress stage1 6400/14997 sec_per_output=2.21 eta_h=5.3
translation-v2 2026-11-25T04:56:54+05:00: progress stage1 6800/14997 sec_per_output=2.34 eta_h=5.3
translation-v2 2026-11-25T04:58:31+05:00: progress stage1 6800/14997 sec_per_output=2.34 eta_h=5.3
translation-v2 2026-11-25T05:26:54+05:00: progress stage1 7200/14997 sec_per_output=2.46 eta_h=5.3
translation-v2 2026-11-25T05:28:32+05:00: progress stage1 7200/14997 sec_per_output=2.46 eta_h=5.3
translation-v2 2026-11-25T05:56:55+05:00: progress stage1 8600/14997 sec_per_output=2.29 eta_h=4.1
translation-v2 2026-11-25T05:58:32+05:00: progress stage1 8700/14997 sec_per_output=2.28 eta_h=4.0
translation-v2 2026-11-25T06:26:55+05:00: progress stage1 9500/14997 sec_per_output=2.25 eta_h=3.4
translation-v2 2026-11-25T06:28:32+05:00: progress stage1 9500/14997 sec_per_output=2.25 eta_h=3.4
translation-v2 2026-11-25T06:56:56+05:00: progress stage1 10500/14997 sec_per_output=2.22 eta_h=2.8
translation-v2 2026-11-25T06:58:33+05:00: progress stage1 10600/14997 sec_per_output=2.20 eta_h=2.7
translation-v2 2026-11-25T07:26:56+05:00: progress stage1 12600/14997 sec_per_output=1.99 eta_h=1.3
translation-v2 2026-11-25T07:28:33+05:00: progress stage1 12600/14997 sec_per_output=1.99 eta_h=1.3
translation-v2 2026-11-25T07:56:57+05:00: progress stage1 13000/14997 sec_per_output=2.05 eta_h=1.1
translation-v2 2026-11-25T07:58:33+05:00: progress stage1 13000/14997 sec_per_output=2.05 eta_h=1.1
translation-v2 2026-11-25T08:26:57+05:00: progress stage1 13500/14997 sec_per_output=2.12 eta_h=0.9
translation-v2 2026-11-25T08:28:34+05:00: progress stage1 13500/14997 sec_per_output=2.12 eta_h=0.9
translation-v2 2026-11-25T08:56:58+05:00: progress stage1 13900/14997 sec_per_output=2.19 eta_h=0.7
translation-v2 2026-11-25T08:58:34+05:00: progress stage1 13900/14997 sec_per_output=2.19 eta_h=0.7
translation-v2 2026-11-25T09:26:58+05:00: progress stage1 14300/14997 sec_per_output=2.24 eta_h=0.4
translation-v2 2026-11-25T09:28:34+05:00: progress stage1 14300/14997 sec_per_output=2.24 eta_h=0.4
translation-v2 2026-11-25T09:56:58+05:00: progress stage1 14800/14997 sec_per_output=2.30 eta_h=0.1
translation-v2 2026-11-25T09:58:35+05:00: progress stage1 14800/14997 sec_per_output=2.30 eta_h=0.1
translation-v2 2026-11-25T10:26:59+05:00: progress stage2 1200/4525 sec_per_output=0.57 eta_h=0.5
translation-v2 2026-11-25T10:28:35+05:00: progress stage2 1200/4525 sec_per_output=0.57 eta_h=0.5
translation-v2 2026-11-25T10:56:59+05:00: progress stage2 1900/4525 sec_per_output=1.46 eta_h=1.1
translation-v2 2026-11-25T10:58:35+05:00: progress stage2 1900/4525 sec_per_output=1.46 eta_h=1.1
translation-v2 2026-11-25T11:27:00+05:00: progress stage2 2400/4525 sec_per_output=1.76 eta_h=1.0
translation-v2 2026-11-25T11:28:36+05:00: progress stage2 2500/4525 sec_per_output=1.86 eta_h=1.0
translation-v2 2026-11-25T11:57:00+05:00: progress stage2 2900/4525 sec_per_output=2.16 eta_h=1.0
translation-v2 2026-11-25T11:58:36+05:00: progress stage2 2900/4525 sec_per_output=2.16 eta_h=1.0
translation-v2 2026-11-25T12:27:01+05:00: progress stage2 3500/4525 sec_per_output=2.34 eta_h=0.7
translation-v2 2026-11-25T12:28:36+05:00: progress stage2 3500/4525 sec_per_output=2.34 eta_h=0.7
translation-v2 2026-11-25T12:57:01+05:00: progress stage2 4000/4525 sec_per_output=2.46 eta_h=0.4
translation-v2 2026-11-25T12:58:37+05:00: progress stage2 4000/4525 sec_per_output=2.46 eta_h=0.4
translation-v2 2026-11-25T13:27:02+05:00: progress stage2 4300/4525 sec_per_output=2.66 eta_h=0.2
translation-v2 2026-11-25T13:28:37+05:00: progress stage2 4400/4525 sec_per_output=2.71 eta_h=0.1
translation-v2 2026-11-25T13:57:02+05:00: progress stage2 4525/4525 sec_per_output=2.75 eta_h=0.0

job: translation-v2
state: done (exit 0)
finished: 2026-11-25T13:57:05+05:00
ollama: stopped
translation-v2 2026-11-25T13:58:37+05:00: progress stage2 4525/4525 sec_per_output=2.75 eta_h=0.0

job: translation-v2
state: done (exit 0)
finished: 2026-11-25T13:58:38+05:00
ollama: stopped

job: translation-eval-v2
state: running (detached container pehredar-translation-eval)
log: logs/translation_eval_v2.log
started: 2026-11-25T17:52:00+05:00
plan: dev_translated_v2 (700 attack + 1,050 benign dev rows), external_translated (425), overrefusal_translated (1,566), each x 3 langs, eval only; Ollama stops when done
translation-eval-v2 2026-11-25T17:53:33+05:00: first start failed (OLLAMA_HOST not set, outputs deleted); restarted with OLLAMA_HOST

job: phase-b-review-support
state: done
result: results/translation_v2_stats.md; data/processed/translation_review_v2_abliterated.csv (30 rows)
phase-c-gate 2026-11-25T17:56:17+05:00: NOT passed (no verdicts in translation_review_v2.csv 0/100 or translation_review_v2_abliterated.csv 0/30); v2 training not started
translation-eval-v2 2026-11-25T18:25:12+05:00: progress dev_translated_v2 stage1 1200/5250 sec_per_output=1.50 eta_h=1.7
translation-eval-v2 2026-11-25T18:55:12+05:00: progress dev_translated_v2 stage1 1700/5250 sec_per_output=2.04 eta_h=2.0
translation-eval-v2 2026-11-25T19:25:13+05:00: progress dev_translated_v2 stage1 2100/5250 sec_per_output=2.58 eta_h=2.3
translation-eval-v2 2026-11-25T19:55:13+05:00: progress dev_translated_v2 stage1 3300/5250 sec_per_output=2.17 eta_h=1.2
translation-eval-v2 2026-11-25T20:25:14+05:00: progress dev_translated_v2 stage1 4400/5250 sec_per_output=2.03 eta_h=0.5
translation-eval-v2 2026-11-25T20:55:14+05:00: progress dev_translated_v2 stage1 4800/5250 sec_per_output=2.23 eta_h=0.3
translation-eval-v2 2026-11-25T21:25:15+05:00: progress dev_translated_v2 stage1 5200/5250 sec_per_output=2.40 eta_h=0.0
translation-eval-v2 2026-11-25T21:55:16+05:00: progress dev_translated_v2 stage2 600/1314 sec_per_output=2.31 eta_h=0.5
translation-eval-v2 2026-11-25T22:25:17+05:00: progress dev_translated_v2 stage2 1100/1314 sec_per_output=3.08 eta_h=0.2
translation-eval-v2 2026-11-25T22:55:18+05:00: progress external_translated stage1 500/1275 sec_per_output=1.60 eta_h=0.3
translation-eval-v2 2026-11-25T23:25:18+05:00: progress external_translated stage1 1100/1275 sec_per_output=2.43 eta_h=0.1
translation-eval-v2 2026-11-25T23:55:20+05:00: progress external_translated stage2 400/513 sec_per_output=2.80 eta_h=0.1
translation-eval-v2 2026-11-26T00:25:20+05:00: progress overrefusal_translated stage1 1400/4698 sec_per_output=1.00 eta_h=0.9
translation-eval-v2 2026-11-26T00:55:21+05:00: progress overrefusal_translated stage1 3400/4698 sec_per_output=0.95 eta_h=0.3
translation-eval-v2 2026-11-26T01:25:21+05:00: progress overrefusal_translated stage2 294/294 sec_per_output=1.62 eta_h=0.0

job: translation-eval-v2
state: done (exit 0)
finished: 2026-11-26T01:25:24+05:00
ollama: stopped
