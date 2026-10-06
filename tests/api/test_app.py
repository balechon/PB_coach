from fastapi.testclient import TestClient

from pb_coach.api.app import app


def test_health():
    respuesta = TestClient(app).get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
