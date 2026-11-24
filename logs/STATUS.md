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
