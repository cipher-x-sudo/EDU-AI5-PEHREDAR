# Pehredar

Pehredar is a local, model-agnostic LLM firewall for English, Urdu, Roman Urdu, and code-mixed traffic.

## Docker setup

Docker Desktop must run with its WSL 2 backend and NVIDIA GPU support. Python 3.11 and Ollama run in containers; no host installation is required.

```powershell
cd E:\EDU\AI\pehredar
python -c "from pathlib import Path; import secrets; p=Path('.env'); p.write_text('PEHREDAR_CANARY=PEHREDAR-'+secrets.token_hex(24)+'\nPEHREDAR_ADMIN_TOKEN='+secrets.token_urlsafe(32)+'\n') if not p.exists() else None"
docker compose up -d --build
docker compose exec ollama ollama pull richardyoung/qwen3-8b-abliterated:Q4_K_M
docker compose exec ollama ollama pull hf.co/QuantFactory/Qwen3Guard-Gen-0.6B-GGUF:Q4_K_M
docker compose run --rm --build tests
```

The canary is stored in `.env`, which is ignored by Git. Ollama models and gateway logs use Docker volumes. The gateway listens on `127.0.0.1:8000`.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$body = @{ model = "richardyoung/qwen3-8b-abliterated:Q4_K_M"; messages = @(@{ role = "user"; content = "Hello" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/chat/completions -Method Post -ContentType application/json -Body $body
```

Stop without deleting model or log volumes: `docker compose down`.

## Current implementation

The Docker stack currently includes:

- FastAPI gateway with an OpenAI-style chat endpoint, forwarding allowed requests to a local model
- L0 Unicode/invisible-character normalization and bounded encoded-payload decoding
- L1 transparent rules for a small set of common prompt-injection phrases
- Per-request decision logging in SQLite
- Health and inspection endpoints
- Basic output canary and secret blocking plus Pakistani CNIC, mobile, IBAN, and email redaction
- Local Qwen3Guard output safety classification with safe, controversial, and unsafe decisions
- Hashed session IDs and bounded escalation-score history
- Confirmed canary misses enter a capped exact-match attack memory when `x-session-id` is provided
- Warning decisions enter a hash-only human review queue; admin-approved attacks enter exact-match memory
- Grouped training script and optional XLM-R classifier adapter
- Read-only dashboard for decision counts, latency, language, and hashes
- Deterministic tests for the first security boundary

The default upstream outside Docker is Ollama at `http://127.0.0.1:11434/v1`. Docker Compose sets it to the internal Ollama service. Allowed requests require a configured canary. The gateway inserts it into the protected model's system prompt and blocks any response containing it.

This is a research prototype. The rules are narrow; a trained multilingual classifier, semantic memory, automatic retraining with a promotion workflow, full baseline comparisons, and final evaluation still depend on reviewed data and additional implementation. Streaming requests receive HTTP 501, and supported chat messages are text-only. Human test-set collection is described in [DATA_COLLECTION.md](DATA_COLLECTION.md); no baseline results are claimed yet.

The review endpoints require `Authorization: Bearer <PEHREDAR_ADMIN_TOKEN>` from `.env`. `GET /v1/review` lists pending item hashes and risk scores; `POST /v1/review` accepts `{"id": 1, "label": "attack", "reviewer": "reviewer-code", "text": "<original text>"}` or `label: "benign"`. Reviewers inspect the original request in their consented local collection workflow and submit it for hash verification; the gateway never saves the submitted text.

`GET /v1/policy` shows the active policy; `PUT /v1/policy` validates and persists a policy with the same admin token. `GET /v1/models` lists versioned classifier directories and the active classifier. The gateway records language, component scores, and per-layer latency with hashed text.

Start the local read-only dashboard with `docker compose --profile dashboard up -d --build dashboard` and open `http://127.0.0.1:8501`. It shows decision counts, recent hashes, and pending review count.

Run a labeled local attack set with `python -m scripts.run_local_attacks data/processed/attacks.jsonl data/processed/local_scan.json`. The runner accepts only `localhost` or `127.0.0.1` and writes IDs and outcomes without prompt text.

## Classifier training

After collecting licensed, labeled training data in `data/processed/train.jsonl`, check it against the frozen human set, then train in a GPU container:

```powershell
python -m scripts.check_split data/processed/train.jsonl data/frozen_test/human_v1.jsonl
docker compose run --rm --build training
```

The training script keeps related examples in one split, chooses its threshold on development examples, and saves the model, tokenizer, preprocessing version, dataset hash, and report together. The frozen set is refused as a training input. Training has not run because the project does not yet have reviewed labeled examples. To serve a trained model in Docker, change the `gateway` build target in `compose.yaml` to `classifier-gateway`, add `PEHREDAR_CLASSIFIER_DIR=/app/models/clf_v1` to `.env`, and rebuild. The classifier gateway requires enough host RAM and may have a large image.

## Host development (optional)

```powershell
cd E:\EDU\AI\pehredar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
ollama pull llama3.2:3b
uvicorn pehredar.app:app --reload --port 8000
```

Try the gateway:

```powershell
curl http://127.0.0.1:8000/health
$body = @{ model = "llama3.2:3b"; messages = @(@{ role = "user"; content = "hello" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/chat/completions -Method Post -ContentType application/json -Body $body
```

Run checks with `pytest`.
