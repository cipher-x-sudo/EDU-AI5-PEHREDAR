import re

import httpx


async def classify_safety(text: str, model: str, upstream_url: str) -> tuple[str, list[str]]:
    """Qwen3Guard verdict: ("safe" | "controversial" | "unsafe", categories such as ["Jailbreak"])."""
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{upstream_url}/chat/completions",
            json={
                "model": model,
                "stream": False,
                "temperature": 0,
                "messages": [{"role": "user", "content": text[:12000]}],
            },
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    match = re.search(r"^\s*Safety:\s*(Safe|Controversial|Unsafe)\b", answer, re.I)
    if not match:
        raise ValueError("Guard model returned no safety class")
    cats = re.search(r"^\s*Categories:\s*(.+)$", answer, re.I | re.M)
    categories = [c.strip() for c in cats.group(1).split(",") if c.strip() and c.strip().lower() != "none"] if cats else []
    return match.group(1).lower(), categories
