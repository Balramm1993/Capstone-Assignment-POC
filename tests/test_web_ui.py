import json

import pytest

from web_ui import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_features(client):
    r = client.get("/features")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)
    assert "a" in data and "b" in data


def test_generate_and_outputs(client):
    r = client.get("/generate")
    assert r.status_code == 200
    data = r.get_json()
    assert "a" in data and "b" in data


def test_feature_cases_ac6(client):
    r = client.get("/feature/a/cases?ac=AC6")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("feature") == "User Login"
    assert data.get("count") >= 1


def test_feature_coverage(client):
    r = client.get("/feature/a/coverage")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)


def test_outputs_list(client):
    r = client.get("/outputs")
    assert r.status_code == 200
    data = r.get_json()
    assert "outputs" in data
