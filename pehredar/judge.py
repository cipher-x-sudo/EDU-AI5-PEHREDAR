import re

import httpx


async def classify_safety(text: str, model: str, upstream_url: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{upstream_url}/chat/completions",
            json={
                "model": model,
                "stream": False,
                "messages": [{"role": "user", "content": text[:12000]}],
            },
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    match = re.search(r"^\s*Safety:\s*(Safe|Controversial|Unsafe)\b", answer, re.I)
    if not match:
        raise ValueError("Guard model returned no safety class")
    return match.group(1).lower()
