# v1 Evaluation Status

v1b one-epoch training completed on CUDA with 5.24 GB peak VRAM. The source-separated evaluation was started but stopped because the CPU ProtectAI DeBERTa pass over the expanded 62,350-row data exceeded the practical runtime window. No accuracy claim is made and no model is promoted.

The final comparison must report these separate rows: `dev_public`, `external_eval`, `bipia (unseen)`, `injecagent (unseen)`, `llmail (seen)`, `xstest FPR`, `or_bench FPR`, and `benign_email_probe FPR`.
