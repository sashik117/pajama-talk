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
    assert word["status"] == "learning"
    assert word["translation"] == "затишний"

    reviewed = client.post(f"/words/{word['id']}/review", headers=headers, json={"grade": "remember"})
    assert reviewed.status_code == 200
    assert reviewed.json()["repetitions"] == 1

    deleted = client.delete(f"/words/{word['id']}", headers=headers)
    assert deleted.status_code == 204
    words = client.get("/words?language_code=en", headers=headers)
    assert words.status_code == 200
    assert words.json() == []


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


def test_engagement_widgets(client: TestClient) -> None:
    headers = auth_headers(client)
    client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "cozy", "language_code": "en", "source_context": "a cozy night"},
    )

    oracle = client.get("/engagement/oracle?language_code=en&target_language_code=uk", headers=headers)
    assert oracle.status_code == 200
    assert oracle.json()["idioms"]

    slang = client.get("/engagement/slang?language_code=en", headers=headers)
    assert slang.status_code == 200
    assert slang.json()["term"]

    puzzle = client.get("/engagement/meme-puzzle?language_code=en", headers=headers)
    assert puzzle.status_code == 200
    assert puzzle.json()["target_word"] == "cozy"
    assert puzzle.json()["pieces"]


def test_meme_puzzle_skips_harsh_terms(client: TestClient) -> None:
    headers = auth_headers(client)
    client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "holy shit", "language_code": "en", "source_context": "rough slang"},
    )

    response = client.get("/engagement/meme-puzzle?language_code=en", headers=headers)
    assert response.status_code == 200
    assert response.json()["target_word"] == "cozy"


def test_meme_puzzle_skips_phrase_terms(client: TestClient) -> None:
    headers = auth_headers(client)
    client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "it hits different", "language_code": "en", "source_context": "slang phrase"},
    )

    response = client.get("/engagement/meme-puzzle?language_code=en", headers=headers)
    assert response.status_code == 200
    assert response.json()["target_word"] == "cozy"


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
            "ai_tone": "Precise examiner",
            "current_level": "A1",
            "target_level": "B2",
            "effort_level": "Intense",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["active_language_code"] == "fr"
    assert body["native_language_code"] == "uk"
    assert body["learning_vibe"] == "Normal"
    assert body["daily_vibe_minutes"] == 15
    assert body["ai_tone"] == "Precise examiner"
    assert body["current_level"] == "A1"
    assert body["target_level"] == "B2"
    assert body["effort_level"] == "Intense"

    profile = client.get("/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["active_language_code"] == "fr"


def test_profile_stats_follow_active_language(client: TestClient) -> None:
    headers = auth_headers(client)
    client.post("/words/enrich", headers=headers, json={"term": "cozy", "language_code": "en"})
    client.post("/words/enrich", headers=headers, json={"term": "spoko", "language_code": "pl"})
    client.patch(
        "/auth/me",
        headers=headers,
        json={"active_language_code": "pl", "learning_vibe": "Hardcore", "daily_vibe_minutes": 30},
    )

    response = client.get("/stats/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["active_language_code"] == "pl"
    assert body["total_words"] == 2
    assert body["language_words"] == 1
    assert body["daily_vibe_minutes"] == 30


def test_speaking_hints_use_active_language_context(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/speaking/hints",
        headers=headers,
        json={
            "room_id": "coffee-alex",
            "last_message": "What should I say next?",
            "language_code": "es",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"simple", "conversational", "spicy"}
    assert body["simple"]


def test_speaking_websocket_streams_reply(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text("Could I get a latte?")
        tokens: list[str] = []
        while True:
            event = websocket.receive_json()
            if event["type"] == "done":
                break
            assert event["type"] == "token"
            tokens.append(event["value"])

    assert "".join(tokens).strip().startswith("Nice choice")


def test_speaking_websocket_uses_mood(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex&mood=tired") as websocket:
        websocket.send_text("Could I get a latte?")
        tokens: list[str] = []
        while True:
            event = websocket.receive_json()
            if event["type"] == "done":
                break
            assert event["type"] == "token"
            tokens.append(event["value"])

    assert "легкий режим" in "".join(tokens)


def test_speaking_websocket_responds_to_ping(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text('{"type":"ping"}')
        event = websocket.receive_json()

    assert event["type"] == "pong"


def test_speaking_echo_feedback(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/speaking/echo",
        headers=headers,
        json={"phrase": "It hits different", "transcript": "it hits different", "language_code": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 100
    assert body["feedback"]


def test_speaking_websocket_uses_learning_words(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")
    client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "cozy", "language_code": "en", "source_context": "This cafe is cozy."},
    )

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text("Could I get a latte?")
        tokens: list[str] = []
        while True:
            event = websocket.receive_json()
            if event["type"] == "done":
                break
            assert event["type"] == "token"
            tokens.append(event["value"])

    assert "cozy" in "".join(tokens)


def test_voice_websocket_turn_and_summary(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/voice-ws?token={token}&room_id=coffee-alex") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "session_ready"
        websocket.send_json({"type": "user_text", "value": "Could I get a latte?", "speed": 0.9})
        tokens: list[str] = []
        tts_event = None
        while True:
            event = websocket.receive_json()
            if event["type"] == "assistant_token":
                tokens.append(event["value"])
            if event["type"] == "tts":
                tts_event = event
            if event["type"] == "done":
                break
        assert "".join(tokens).strip().startswith("Nice choice")
        assert tts_event["format"] == "client_speech_synthesis"
        assert tts_event["provider"] == "client_speech_synthesis"

        websocket.send_json({"type": "end_call"})
        summary = websocket.receive_json()
        assert summary["type"] == "call_summary"
        assert summary["value"]["turns"] == 1
        assert summary["value"]["new_phrases"]


def test_voice_websocket_accepts_audio_chunk_turn(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/voice-ws?token={token}&room_id=coffee-alex") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "session_ready"
        assert ready["capabilities"]["accepts_audio_chunks"] is True

        websocket.send_json({"type": "audio_chunk", "audio_base64": "ZmFrZS1hdWRpbw==", "transcript": "Could I get a latte?"})
        status = websocket.receive_json()
        assert status["type"] == "stt_status"
        assert status["chunks"] == 1
        assert status["bytes"] == 10

        websocket.send_json({"type": "end_audio", "speed": 0.85})
        transcript = websocket.receive_json()
        assert transcript["type"] == "transcript"
        assert transcript["value"] == "Could I get a latte?"
        assert transcript["provider"] == "audio_chunk_metadata"

        events: list[dict[str, object]] = []
        while True:
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "done":
                break

        tts = next(event for event in events if event["type"] == "tts")
        assert tts["speed"] == 0.85
        assert tts["provider"] == "client_speech_synthesis"


def test_voice_websocket_rejects_empty_audio_turn(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/voice-ws?token={token}&room_id=coffee-alex") as websocket:
        assert websocket.receive_json()["type"] == "session_ready"
        websocket.send_json({"type": "audio_chunk", "audio_base64": ""})
        assert websocket.receive_json()["type"] == "stt_status"
        websocket.send_json({"type": "end_audio"})
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert "No speech" in event["value"]


def test_voice_websocket_responds_to_ping(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/voice-ws?token={token}&room_id=coffee-alex") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "session_ready"
        websocket.send_json({"type": "ping"})
        event = websocket.receive_json()

    assert event["type"] == "pong"


def test_grammar_drop_responds_to_speaking_mistake(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text("Yesterday I have went to the cafe.")
        while websocket.receive_json()["type"] != "done":
            pass

    response = client.get("/grammar/drops", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == "present-perfect-rescue"


def test_grammar_topics_and_checker(client: TestClient) -> None:
    headers = auth_headers(client)

    topics = client.get("/grammar/topics", headers=headers)
    assert topics.status_code == 200
    body = topics.json()
    assert body[0]["id"] == "articles-a-an-the"
    assert body[0]["exercises"][0]["options"]

    correct = client.post(
        "/grammar/check",
        headers=headers,
        json={"topic_id": "articles-a-an-the", "exercise_id": "art-1", "answer": "an"},
    )
    assert correct.status_code == 200
    assert correct.json()["correct"] is True

    wrong = client.post(
        "/grammar/check",
        headers=headers,
        json={"topic_id": "articles-a-an-the", "exercise_id": "art-1", "answer": "a"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert wrong.json()["expected"] == "an"


def test_grammar_topics_prioritize_speaking_mistakes(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text("If I will finish early, I will text you.")
        while websocket.receive_json()["type"] != "done":
            pass

    topics = client.get("/grammar/topics", headers=headers)
    assert topics.status_code == 200
    body = topics.json()
    assert body[0]["id"] == "conditionals-real-future"
    assert body[0]["recommended"] is True


def test_learning_path_and_grammar_follow_selected_language(client: TestClient) -> None:
    headers = auth_headers(client)
    client.patch("/auth/me", headers=headers, json={"active_language_code": "pl"})

    path = client.get("/learning/path?language_code=pl", headers=headers)
    assert path.status_code == 200
    path_body = path.json()
    assert path_body["language_code"] == "pl"
    assert "Poproszę kawę" in path_body["next_room_prompt"]

    client.patch(
        "/auth/me",
        headers=headers,
        json={"current_level": "B1", "target_level": "C1", "effort_level": "Intense"},
    )
    personalized = client.get("/learning/path?language_code=pl", headers=headers)
    assert personalized.status_code == 200
    personalized_body = personalized.json()
    assert "B1 -> C1" in personalized_body["level"]
    assert personalized_body["steps"][0]["id"] == "pl-question"
    assert "3-turn mini dialogue" in personalized_body["steps"][0]["micro_task"]

    topics = client.get("/grammar/topics?language_code=pl", headers=headers)
    assert topics.status_code == 200
    topic_body = topics.json()
    assert topic_body[0]["id"].startswith("pl-")
    assert "Poproszę kawę." in str(topic_body)

    check = client.post(
        "/grammar/check",
        headers=headers,
        json={"topic_id": "pl-requests", "exercise_id": "pl-request-1", "answer": "Poproszę kawę."},
    )
    assert check.status_code == 200
    assert check.json()["correct"] is True


def test_ukrainian_and_russian_can_be_learning_languages(client: TestClient) -> None:
    headers = auth_headers(client)

    ukrainian = client.get("/learning/path?language_code=uk&target_language_code=ru", headers=headers)
    assert ukrainian.status_code == 200
    ukrainian_body = ukrainian.json()
    assert ukrainian_body["language_code"] == "uk"
    assert "Я хочу каву" in ukrainian_body["next_room_prompt"]
    assert "учитель" in ukrainian_body["assistant_role"]

    russian_rooms = client.get("/speaking/rooms?language_code=ru&target_language_code=uk", headers=headers)
    assert russian_rooms.status_code == 200
    assert "Привет, я Саша" in russian_rooms.json()[0]["prompt"]
    assert "Я хочу кофе" in russian_rooms.json()[0]["prompt"]


def test_speaking_uses_selected_language_starter_pack(client: TestClient) -> None:
    headers = auth_headers(client)
    token = headers["Authorization"].replace("Bearer ", "")
    client.patch("/auth/me", headers=headers, json={"active_language_code": "es"})

    rooms = client.get("/speaking/rooms?language_code=es", headers=headers)
    assert rooms.status_code == 200
    assert "Quiero un café" in rooms.json()[0]["prompt"]

    hints = client.post(
        "/speaking/hints",
        headers=headers,
        json={"room_id": "coffee-alex", "last_message": "Hola", "language_code": "es"},
    )
    assert hints.status_code == 200
    assert hints.json()["simple"] == "Gracias, suena bien."

    with client.websocket_connect(f"/speaking/ws?token={token}&room_id=coffee-alex") as websocket:
        websocket.send_text("Hola")
        tokens: list[str] = []
        while True:
            event = websocket.receive_json()
            if event["type"] == "done":
                break
            tokens.append(event["value"])

    assert "Quiero un café" in "".join(tokens)


def test_review_due_queue_returns_due_words_and_removes_reviewed(client: TestClient) -> None:
    headers = auth_headers(client)
    created = client.post(
        "/words/enrich",
        headers=headers,
        json={"term": "cozy", "language_code": "en"},
    ).json()

    due = client.get("/words/review-due?language_code=en", headers=headers)
    assert due.status_code == 200
    assert [word["id"] for word in due.json()] == [created["id"]]

    client.post(f"/words/{created['id']}/review", headers=headers, json={"grade": "remember"})
    due_after_review = client.get("/words/review-due?language_code=en", headers=headers)
    assert due_after_review.status_code == 200
    assert due_after_review.json() == []
