import importlib

from fastapi.testclient import TestClient

gateway = importlib.import_module("pehredar.app")
client = TestClient(gateway.app)


def test_policy_update_requires_admin_and_valid_thresholds(monkeypatch, tmp_path):
    monkeypatch.setattr(gateway, "DB_PATH", tmp_path / "policy.db")
    monkeypatch.setattr(gateway, "ADMIN_TOKEN", "test-admin")
    gateway.init_db()
    original = gateway.POLICY
    payload = {"tenant": "test", "thresholds": {"warn": 0.4, "judge_low": 0.25, "block": 0.8}}
    try:
        assert client.put("/v1/policy", json=payload).status_code == 401
        response = client.put("/v1/policy", json=payload, headers={"Authorization": "Bearer test-admin"})
        assert response.status_code == 200
        assert client.get("/v1/policy").json()["thresholds"]["block"] == 0.8
        payload["thresholds"]["warn"] = 0.9
        assert client.put("/v1/policy", json=payload, headers={"Authorization": "Bearer test-admin"}).status_code == 422
    finally:
        monkeypatch.setattr(gateway, "POLICY", original)


def test_models_endpoint_lists_versioned_artifacts(monkeypatch, tmp_path):
    model_dir = tmp_path / "clf_v1"
    model_dir.mkdir()
    (model_dir / "training_report.json").write_text("{}")
    monkeypatch.setattr(gateway, "MODELS_DIR", tmp_path)
    assert client.get("/v1/models").json()["candidates"] == ["clf_v1"]
