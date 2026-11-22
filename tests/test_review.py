import importlib

from fastapi.testclient import TestClient
from pehredar.memory import is_known_attack

gateway = importlib.import_module("pehredar.app")
client = TestClient(gateway.app)


def test_review_requires_admin_and_only_confirmed_attacks_enter_memory(monkeypatch, tmp_path):
    monkeypatch.setattr(gateway, "DB_PATH", tmp_path / "events.db")
    monkeypatch.setattr(gateway, "ADMIN_TOKEN", "local-test-admin")
    monkeypatch.setattr(gateway, "score_rules", lambda text: (0.5, ["uncertain_rule"]))
    gateway.init_db()

    assert client.get("/v1/review").status_code == 401
    assert client.post("/v1/check/input", json={
        "messages": [{"role": "user", "content": "First uncertain example"}]
    }).json()["action"] == "warn"
    headers = {"Authorization": "Bearer local-test-admin"}
    items = client.get("/v1/review", headers=headers).json()["items"]
    assert len(items) == 1
    assert "First uncertain example" not in str(items)
    assert client.post("/v1/review", headers=headers, json={
        "id": items[0]["id"], "label": "attack", "reviewer": "tester", "text": "wrong text"
    }).status_code == 400
    assert client.post("/v1/review", headers=headers, json={
        "id": items[0]["id"], "label": "benign", "reviewer": "tester",
        "text": "First uncertain example",
    }).status_code == 200
    assert not is_known_attack(gateway.DB_PATH, "First uncertain example")

    client.post("/v1/check/input", json={
        "messages": [{"role": "user", "content": "Second uncertain example"}]
    })
    attack = client.get("/v1/review", headers=headers).json()["items"][0]
    assert client.post("/v1/review", headers=headers, json={
        "id": attack["id"], "label": "attack", "reviewer": "tester",
        "text": "Second uncertain example",
    }).status_code == 200
    monkeypatch.setattr(gateway, "score_rules", lambda text: (0.0, []))
    assert gateway.inspect_text("Second uncertain example", record=False).action == "block"
    assert client.get("/v1/review", headers=headers).json()["items"] == []
