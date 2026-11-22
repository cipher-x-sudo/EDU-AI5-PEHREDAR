import argparse
import json
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx

from pehredar.dataset import load_jsonl


def run(dataset: Path, output: Path, gateway_url: str, model: str) -> dict:
    parsed = urlparse(gateway_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Attack runner only accepts a local HTTP gateway")
    rows = load_jsonl(dataset)
    results = []
    with httpx.Client(timeout=180) as client:
        for row in rows:
            if row.label != "attack":
                continue
            response = client.post(
                f"{gateway_url.rstrip('/')}/v1/chat/completions",
                headers={"x-session-id": f"redteam-{uuid.uuid4().hex}"},
                json={"model": model, "messages": [{"role": "user", "content": row.input_text()}]},
            )
            response.raise_for_status()
            body = response.json()
            results.append({
                "id": row.id,
                "lang": row.lang,
                "type": row.type,
                "blocked": body["choices"][0]["finish_reason"] == "content_filter",
            })
    report = {
        "dataset": str(dataset),
        "count": len(results),
        "blocked": sum(result["blocked"] for result in results),
        "results": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run labeled attacks against a local Pehredar gateway")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="richardyoung/qwen3-8b-abliterated:Q4_K_M")
    args = parser.parse_args()
    result = run(args.dataset, args.output, args.gateway_url, args.model)
    print(f"Blocked {result['blocked']} of {result['count']} attacks")
