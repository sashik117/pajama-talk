from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={"email": "dreamer@example.com", "password": "supersecret", "display_name": "Dreamer"},
    )
    if response.status_code == 409:
        response = client.post("/auth/login", json={"email": "dreamer@example.com", "password": "supersecret"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_word_enrichment_and_review(client: TestClient) -> None:
    headers = auth_headers(client)
    created = client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "cozy", "language_code": "en", "source_context": "a cozy night"},
    )
    assert created.status_code == 201
    word = created.json()
    assert word["term"] == "cozy"
    assert word["language_code"] == "en"
    assert word["translation"] == "затишний"

    reviewed = client.post(f"/words/{word['id']}/review", headers=headers, json={"grade": "remember"})
    assert reviewed.status_code == 200
    assert reviewed.json()["repetitions"] == 1


def test_context_buddy(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/context/analyze",
        headers=headers,
        json={"text": "This deadline is awkward but the vibe is cozy."},
    )
    assert response.status_code == 200
    body = response.json()
    assert "deadline" in body["suggested_words"]


def test_words_can_be_filtered_by_learning_language(client: TestClient) -> None:
    headers = auth_headers(client)
    english = client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "cozy", "language_code": "en"},
    )
    polish = client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "spoko", "language_code": "pl"},
    )

    assert english.status_code == 201
    assert polish.status_code == 201

    response = client.get("/words?language_code=pl", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert [word["term"] for word in body] == ["spoko"]
    assert body[0]["language_code"] == "pl"


def test_profile_update_persists_language_and_vibe(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.patch(
        "/auth/me",
        headers=headers,
        json={
            "active_language_code": "fr",
            "native_language_code": "uk",
            "learning_vibe": "Normal",
            "daily_vibe_minutes": 15,
            "ai_tone": "strict British aristocrat",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["active_language_code"] == "fr"
    assert body["native_language_code"] == "uk"
    assert body["learning_vibe"] == "Normal"
    assert body["daily_vibe_minutes"] == 15
    assert body["ai_tone"] == "strict British aristocrat"

    profile = client.get("/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["active_language_code"] == "fr"
