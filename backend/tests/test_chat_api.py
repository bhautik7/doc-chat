from unittest.mock import patch

from app.models.chat import ChatSession, Message


def test_chat_endpoints_require_auth(client):
    assert client.post("/chat/sessions").status_code == 401
    assert client.get("/chat/sessions").status_code == 401
    assert client.post("/chat/ask", json={"session_id": 1, "question": "hi"}).status_code == 401


def test_create_session_returns_new_session(client, auth_headers):
    res = client.post("/chat/sessions", headers=auth_headers)

    assert res.status_code == 201
    assert res.json()["id"] is not None
    assert res.json()["title"] == "New Chat"


def test_list_sessions_only_returns_own_sessions(client, auth_headers, current_user, db_session):
    own = client.post("/chat/sessions", headers=auth_headers).json()
    db_session.add(ChatSession(owner_id=current_user.id + 1))
    db_session.commit()

    res = client.get("/chat/sessions", headers=auth_headers)

    assert res.status_code == 200
    assert [s["id"] for s in res.json()] == [own["id"]]


def test_get_messages_returns_session_history(client, auth_headers, db_session):
    session_id = client.post("/chat/sessions", headers=auth_headers).json()["id"]
    db_session.add_all(
        [
            Message(session_id=session_id, role="user", content="question?"),
            Message(session_id=session_id, role="assistant", content="answer", sources="[]"),
        ]
    )
    db_session.commit()

    res = client.get(f"/chat/sessions/{session_id}/messages", headers=auth_headers)

    assert res.status_code == 200
    assert [(m["role"], m["content"]) for m in res.json()] == [
        ("user", "question?"),
        ("assistant", "answer"),
    ]


def test_get_messages_rejects_unknown_session(client, auth_headers):
    res = client.get("/chat/sessions/999/messages", headers=auth_headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Chat session not found"


def test_get_messages_rejects_session_owned_by_another_user(client, auth_headers, current_user, db_session):
    other = ChatSession(owner_id=current_user.id + 1)
    db_session.add(other)
    db_session.commit()

    res = client.get(f"/chat/sessions/{other.id}/messages", headers=auth_headers)

    assert res.status_code == 404


@patch("app.api.chat.ask_question")
def test_ask_returns_assistant_message(mock_ask, client, auth_headers, current_user, db_session):
    session_id = client.post("/chat/sessions", headers=auth_headers).json()["id"]

    def fake_ask(db, user_id, sid, question, document_ids):
        message = Message(session_id=sid, role="assistant", content="answer", sources="[]")
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    mock_ask.side_effect = fake_ask

    res = client.post(
        "/chat/ask",
        headers=auth_headers,
        json={"session_id": session_id, "question": "Refund policy?", "document_ids": [1]},
    )

    assert res.status_code == 200
    assert res.json()["content"] == "answer"
    assert mock_ask.call_args.args[1:] == (current_user.id, session_id, "Refund policy?", [1])


@patch("app.api.chat.ask_question")
def test_ask_rejects_unknown_session(mock_ask, client, auth_headers):
    res = client.post("/chat/ask", headers=auth_headers, json={"session_id": 999, "question": "hi"})

    assert res.status_code == 404
    mock_ask.assert_not_called()
