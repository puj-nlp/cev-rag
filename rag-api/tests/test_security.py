"""Security tests for the frontend API: headers, session binding, CSRF and input validation.

Run from rag-api/:  ENV=production ALLOWED_ORIGINS=https://app.test python -m pytest tests
"""

import os

os.environ.setdefault("ENV", "production")
os.environ.setdefault("ALLOWED_ORIGINS", "https://app.test")
os.environ.setdefault("API_KEYS", "")

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.controllers.frontend_controller import FrontendController
from src.adapters.repositories.memory_chat_repository import InMemoryChatSessionRepository
from src.application.use_cases import ChatSessionUseCase
from src.domain.entities import Message
from src.domain.ports import TimestampService
from src.infrastructure.security import SESSION_COOKIE_NAME, SecurityHeadersMiddleware

ORIGIN = "https://app.test"
CSRF = {"X-Requested-With": "cev-rag", "Origin": ORIGIN}


class FixedTimestampService(TimestampService):
    def get_current_timestamp(self) -> str:
        return datetime(2026, 1, 1).isoformat()


class EchoQuestionAnsweringUseCase:
    """Stand-in for the RAG pipeline: echoes the requested language."""

    def __init__(self):
        self.last_question = None

    async def process_question(self, question, use_tools=True):
        self.last_question = question
        return Message(content=f"answer:{question.language}", is_bot=True)


@pytest.fixture
def qa():
    return EchoQuestionAnsweringUseCase()


@pytest.fixture
def app(qa):
    chat_use_case = ChatSessionUseCase(InMemoryChatSessionRepository(), FixedTimestampService())
    application = FastAPI()
    application.add_middleware(SecurityHeadersMiddleware)
    application.include_router(FrontendController(chat_use_case, qa).router, prefix="/api")
    return application


def new_client(app):
    # https base URL so the Secure session cookie is sent back
    return TestClient(app, base_url="https://app.test")


def test_security_headers_present(app):
    response = new_client(app).get("/api/frontend/chats", headers={"Referer": ORIGIN + "/es/chat"})
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "max-age=" in response.headers["Strict-Transport-Security"]


def test_session_cookie_flags(app):
    response = new_client(app).post("/api/frontend/session", json={}, headers=CSRF)
    cookie = response.headers["set-cookie"].lower()
    assert SESSION_COOKIE_NAME in cookie
    assert "httponly" in cookie and "secure" in cookie and "samesite=strict" in cookie


def test_legacy_session_is_adopted(app):
    legacy = "session_1700000000000_abc123xyz"
    client = new_client(app)
    client.post("/api/frontend/session", json={"legacy_session_id": legacy}, headers=CSRF)
    assert client.cookies.get(SESSION_COOKIE_NAME) == legacy


def test_post_without_csrf_header_is_rejected(app):
    response = new_client(app).post("/api/frontend/chats", json={"title": "x"}, headers={"Origin": ORIGIN})
    assert response.status_code == 403


def test_post_from_foreign_origin_is_rejected(app):
    headers = {"X-Requested-With": "cev-rag", "Origin": "https://evil.test"}
    response = new_client(app).post("/api/frontend/chats", json={"title": "x"}, headers=headers)
    assert response.status_code == 403


def test_spoofed_localhost_host_header_is_rejected_in_production(app):
    client = TestClient(app, base_url="http://localhost:3000")
    response = client.get("/api/frontend/chats")
    assert response.status_code == 403


def test_chats_are_isolated_per_session(app):
    owner, intruder = new_client(app), new_client(app)
    chat = owner.post("/api/frontend/chats", json={"title": "mine"}, headers=CSRF).json()

    assert owner.get(f"/api/frontend/chats/{chat['id']}", headers=CSRF).status_code == 200
    assert intruder.get(f"/api/frontend/chats/{chat['id']}", headers=CSRF).status_code == 404
    assert intruder.delete(f"/api/frontend/chats/{chat['id']}", headers=CSRF).status_code == 404
    assert intruder.get("/api/frontend/chats", headers=CSRF).json() == []
    question = {"question": "hola", "language": "es"}
    assert intruder.post(f"/api/frontend/chats/{chat['id']}/messages", json=question, headers=CSRF).status_code == 404


def test_question_validation(app, qa):
    client = new_client(app)
    chat = client.post("/api/frontend/chats", json={"title": "t"}, headers=CSRF).json()
    url = f"/api/frontend/chats/{chat['id']}/messages"

    assert client.post(url, json={"question": "x" * 5000}, headers=CSRF).status_code == 422
    assert client.post(url, json={"question": "   \x00 "}, headers=CSRF).status_code == 422
    assert client.post(url, json={"question": "hi", "language": "fr"}, headers=CSRF).status_code == 422

    response = client.post(url, json={"question": " What is the Paz Grande?\x07 ", "language": "en"}, headers=CSRF)
    assert response.status_code == 200
    assert response.json()["content"] == "answer:en"
    assert qa.last_question.text == "What is the Paz Grande?"


def test_invalid_session_cookie_is_replaced(app):
    client = new_client(app)
    client.cookies.set(SESSION_COOKIE_NAME, "<script>", domain="app.test", path="/api")
    response = client.get("/api/frontend/chats", headers=CSRF)
    assert response.status_code == 200
    assert SESSION_COOKIE_NAME in response.headers.get("set-cookie", "")
