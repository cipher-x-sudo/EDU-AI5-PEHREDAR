import asyncio
import importlib

import httpx
import pytest
from fastapi.testclient import TestClient

from pehredar.judge import classify_safety

gateway = importlib.import_module("pehredar.app")


def test_guard_parses_safety_class(monkeypatch):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Safety: Controversial\nCategories: None"}}]},
        )
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    assert asyncio.run(classify_safety("hello", "guard", "http://ollama/v1")) == ("controversial", [])


def test_guard_rejects_unknown_format(monkeypatch):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"choices": [{"message": {"content": "maybe safe"}}]})
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    with pytest.raises(ValueError):
        asyncio.run(classify_safety("hello", "guard", "http://ollama/v1"))


def test_unsafe_judge_is_recorded_and_blocks_before_protected_model(monkeypatch, tmp_path):
    monkeypatch.setattr(gateway, "DB_PATH", tmp_path / "events.db")
    gateway.init_db()
    monkeypatch.setattr(gateway, "GUARD_MODEL", "local-guard")
    monkeypatch.setattr(gateway, "score_rules", lambda text: (0.5, ["uncertain_rule"]))
    async def unsafe(text, model, upstream_url):
        return "unsafe", ["Violent"]
    monkeypatch.setattr(gateway, "classify_safety", unsafe)
    response = TestClient(gateway.app).post("/v1/chat/completions", json={
        "messages": [{"role": "user", "content": "uncertain example"}]
    })
    assert response.json()["choices"][0]["finish_reason"] == "content_filter"
    import sqlite3
    import json
    with sqlite3.connect(gateway.DB_PATH) as db:
        scores, latencies = db.execute(
            "SELECT component_scores, layer_latency_ms FROM decisions ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert json.loads(scores)["judge"] == 1.0
    assert "judge" in json.loads(latencies)


def test_guard_parses_categories(monkeypatch):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(lambda request: httpx.Response(
        200, json={"choices": [{"message": {"content": "Safety: Unsafe\nCategories: Violent, Jailbreak\n"}}]}))
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    assert asyncio.run(classify_safety("x", "guard", "http://ollama/v1")) == ("unsafe", ["Violent", "Jailbreak"])


@pytest.mark.parametrize("categories,wanted,action", [
    (["Violent"], None, "block"), (["Violent"], ["Jailbreak"], "warn"), (["Jailbreak"], ["Jailbreak"], "block")])
def test_block_categories(monkeypatch, tmp_path, categories, wanted, action):
    monkeypatch.setattr(gateway, "DB_PATH", tmp_path / "events.db"); gateway.init_db()
    monkeypatch.setattr(gateway, "GUARD_MODEL", "local-guard")
    monkeypatch.setattr(gateway, "score_rules", lambda text: (0.5, []))
    async def unsafe(text, model, upstream_url):
        return "unsafe", categories
    monkeypatch.setattr(gateway, "classify_safety", unsafe)
    monkeypatch.setattr(gateway, "POLICY", gateway.POLICY.model_copy(update={"judge": gateway.JudgePolicy(block_categories=wanted)}))
    d = TestClient(gateway.app).post("/v1/check/input", json={"messages": [{"role": "user", "content": "x"}]}).json()
    assert d["action"] == action and f"judge_category:{categories[0]}" in d["tags"]
