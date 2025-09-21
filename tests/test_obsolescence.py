import pytest
from flask import Flask
import requests

from src.routes.obsolescence import obsolescence_bp


class DummyResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON payload provided")
        return self._payload


@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(obsolescence_bp, url_prefix="/api")

    # Évite toute interaction réelle avec la base lors des tests
    monkeypatch.setattr(
        "src.routes.obsolescence.save_obsolescence_info", lambda *args, **kwargs: None
    )

    with app.test_client() as client:
        yield client


def test_check_obsolescence_success(client, monkeypatch):
    sample_payload = [
        {
            "cycle": "1.0",
            "eol": "9999-12-31",
            "support": "9999-12-31",
        }
    ]

    def fake_get(url, timeout):
        return DummyResponse(200, sample_payload)

    monkeypatch.setattr("src.routes.obsolescence.requests.get", fake_get)

    response = client.post(
        "/api/obsolescence/check", json={"product_name": "TestProduit"}
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["product_name"] == "TestProduit"
    assert payload["version"] == "1.0"
    assert payload["is_obsolete"] is False


def test_check_obsolescence_not_found(client, monkeypatch):
    def fake_get(url, timeout):
        return DummyResponse(404, text="Not Found")

    monkeypatch.setattr("src.routes.obsolescence.requests.get", fake_get)

    response = client.post(
        "/api/obsolescence/check", json={"product_name": "Inconnu"}
    )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Produit non trouvé sur endoflife.date"
    }


def test_check_obsolescence_network_failure(client, monkeypatch):
    def fake_get(url, timeout):
        raise requests.Timeout("timeout error")

    monkeypatch.setattr("src.routes.obsolescence.requests.get", fake_get)

    response = client.post(
        "/api/obsolescence/check", json={"product_name": "Any"}
    )

    assert response.status_code == 502
    payload = response.get_json()
    assert payload["error"] == "Erreur réseau lors de la récupération des données d'obsolescence"
    assert "details" in payload
