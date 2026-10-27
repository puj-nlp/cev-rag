"""Domain guardrail tests: intent classification, retrieval threshold and fallback messages.

Run from rag-api/:  python -m pytest tests
"""

import asyncio
from datetime import datetime
from uuid import uuid4

import pytest

from src.adapters.external.openai_guardrail import IntentResult, parse_classifier_output
from src.adapters.repositories.memory_chat_repository import InMemoryChatSessionRepository
from src.application.guardrails import OUT_OF_SCOPE_MESSAGES, SMALL_TALK_MESSAGES, DomainGuardrail
from src.application.use_cases import QuestionAnsweringUseCase
from src.domain.entities import ChatSession, Document, Message, Question
from src.domain.ports import TimestampService

THRESHOLD = 0.35


def run(coro):
    return asyncio.run(coro)


class FixedTimestampService(TimestampService):
    def get_current_timestamp(self) -> str:
        return datetime(2026, 1, 1).isoformat()


class FakeClassifier:
    def __init__(self, result=None, error=False):
        self.result = result
        self.error = error
        self.calls = []

    async def classify(self, question, chat_history):
        self.calls.append((question, chat_history))
        if self.error:
            return None  # OpenAIIntentClassifier returns None when the API fails
        return self.result


class FakeEmbeddingService:
    def __init__(self):
        self.texts = []

    async def generate_embedding(self, text):
        self.texts.append(text)
        return [0.0]


class FakeVectorDatabase:
    def __init__(self, scores):
        self.scores = scores

    async def search_similar_documents(self, embedding, limit=5):
        return [Document(content="fragment", metadata={}, score=score) for score in self.scores]

    async def verify_connection(self):
        return True


class FakeLLMService:
    def __init__(self):
        self.calls = 0

    async def generate_answer_with_tools(self, question, chat_history, language="es"):
        self.calls += 1
        return {"content": f"answer:{language}", "references": []}


def in_scope(query="¿Qué es la Paz Grande?"):
    return IntentResult(in_scope=True, reason="truth commission", standalone_query=query)


def off_topic():
    return IntentResult(in_scope=False, reason="programming", standalone_query="write a python script")


def build(classifier, scores):
    repository = InMemoryChatSessionRepository()
    embeddings = FakeEmbeddingService()
    llm = FakeLLMService()
    guardrail = DomainGuardrail(classifier, embeddings, FakeVectorDatabase(scores), THRESHOLD)
    use_case = QuestionAnsweringUseCase(
        chat_repository=repository,
        vector_db=None,
        embedding_service=embeddings,
        llm_service=llm,
        context_builder=None,
        timestamp_service=FixedTimestampService(),
        guardrail=guardrail,
    )
    chat = ChatSession(uuid4(), "t", "s", [], datetime(2026, 1, 1), datetime(2026, 1, 1))
    run(repository.save(chat))
    return use_case, repository, chat, embeddings, llm


def ask(use_case, chat, text, language="es"):
    return run(use_case.process_question(Question(text=text, chat_id=chat.id, language=language)))


def test_off_topic_intent_is_rejected_without_calling_llm():
    use_case, repository, chat, embeddings, llm = build(FakeClassifier(off_topic()), [0.9])
    message = ask(use_case, chat, "Write me a Python script")

    assert message.out_of_scope is True
    assert message.content == OUT_OF_SCOPE_MESSAGES["es"]
    assert llm.calls == 0
    assert embeddings.texts == []  # rejected before touching the vector store
    stored = run(repository.find_by_id(chat.id))
    assert [m.is_bot for m in stored.messages] == [False, True]
    assert stored.messages[-1].out_of_scope is True


def test_low_relevance_is_rejected():
    use_case, _, chat, _, llm = build(FakeClassifier(in_scope()), [0.2, 0.31])
    message = ask(use_case, chat, "¿Qué es la Paz Grande?")
    assert message.out_of_scope is True
    assert llm.calls == 0


def test_empty_retrieval_is_rejected():
    use_case, _, chat, _, llm = build(FakeClassifier(in_scope()), [])
    assert ask(use_case, chat, "¿Qué es la Paz Grande?").out_of_scope is True
    assert llm.calls == 0


def test_relevant_question_reaches_llm():
    use_case, _, chat, _, llm = build(FakeClassifier(in_scope()), [0.2, THRESHOLD])
    message = ask(use_case, chat, "¿Qué es la Paz Grande?")
    assert message.out_of_scope is False
    assert message.content == "answer:es"
    assert llm.calls == 1


@pytest.mark.parametrize("language", ["es", "en"])
def test_rejection_message_follows_language(language):
    use_case, _, chat, _, _ = build(FakeClassifier(off_topic()), [0.9])
    assert ask(use_case, chat, "Who won the World Cup?", language).content == OUT_OF_SCOPE_MESSAGES[language]


def test_classifier_failure_falls_back_to_threshold():
    use_case, _, chat, embeddings, llm = build(FakeClassifier(error=True), [0.6])
    assert ask(use_case, chat, "¿Qué es la Paz Grande?").out_of_scope is False
    assert embeddings.texts == ["¿Qué es la Paz Grande?"]
    assert llm.calls == 1

    use_case, _, chat, _, llm = build(FakeClassifier(error=True), [0.1])
    assert ask(use_case, chat, "Tell me a joke").out_of_scope is True
    assert llm.calls == 0


def test_standalone_query_is_used_for_retrieval_and_history_excludes_current_question():
    classifier = FakeClassifier(in_scope("¿En qué año se publicó el Informe Final de la Comisión?"))
    use_case, repository, chat, embeddings, _ = build(classifier, [0.7])
    chat.messages.append(Message(content="¿Qué es el Informe Final?", is_bot=False))
    chat.messages.append(Message(content="Es el documento...", is_bot=True))
    run(repository.save(chat))

    ask(use_case, chat, "¿Y en qué año?")
    assert embeddings.texts == ["¿En qué año se publicó el Informe Final de la Comisión?"]
    question, history = classifier.calls[0]
    assert question == "¿Y en qué año?"
    assert [m["content"] for m in history] == ["¿Qué es el Informe Final?", "Es el documento..."]


def test_without_guardrail_everything_reaches_llm():
    use_case, _, chat, _, llm = build(FakeClassifier(off_topic()), [0.0])
    use_case._guardrail = None
    assert ask(use_case, chat, "Write me a Python script").out_of_scope is False
    assert llm.calls == 1


@pytest.mark.parametrize("raw", [None, "", "not json", "[]", '{"reason": "x"}', '{"in_scope": "yes"}'])
def test_malformed_classifier_output_is_ignored(raw):
    assert parse_classifier_output(raw, "q") is None


def test_classifier_output_is_parsed():
    result = parse_classifier_output('{"in_scope": false, "reason": "code", "standalone_query": "  "}', "q")
    assert result == IntentResult(in_scope=False, reason="code", standalone_query="q")


def test_out_of_scope_flag_round_trips_through_sqlite(tmp_path):
    from src.adapters.repositories.sqlite_chat_repository import SQLiteChatSessionRepository

    repository = SQLiteChatSessionRepository(str(tmp_path / "chats.db"))
    chat = ChatSession(uuid4(), "t", "s", [
        Message(content="q", is_bot=False, timestamp=datetime(2026, 1, 1)),
        Message(content="no", is_bot=True, timestamp=datetime(2026, 1, 1), out_of_scope=True),
    ], datetime(2026, 1, 1), datetime(2026, 1, 1))
    run(repository.save(chat))
    stored = run(repository.find_by_id(chat.id))
    assert [m.out_of_scope for m in stored.messages] == [False, True]


def small_talk(reply="¡Hola! Pregúntame sobre el Informe Final."):
    return IntentResult(in_scope=True, reason="greeting", standalone_query="hola", small_talk=True, reply=reply)


def test_small_talk_is_answered_without_retrieval_or_llm():
    use_case, repository, chat, embeddings, llm = build(FakeClassifier(small_talk()), [0.0])
    message = ask(use_case, chat, "hola")

    assert message.out_of_scope is False
    assert message.content == "¡Hola! Pregúntame sobre el Informe Final."
    assert embeddings.texts == []  # greetings never pass the relevance threshold
    assert llm.calls == 0
    stored = run(repository.find_by_id(chat.id))
    assert [m.content for m in stored.messages] == ["hola", message.content]


@pytest.mark.parametrize("language", ["es", "en"])
def test_small_talk_without_reply_uses_default_message(language):
    use_case, _, chat, _, _ = build(FakeClassifier(small_talk(reply="")), [0.0])
    assert ask(use_case, chat, "hello", language).content == SMALL_TALK_MESSAGES[language]


def test_classifier_output_parses_small_talk():
    result = parse_classifier_output(
        '{"in_scope": true, "small_talk": true, "reason": "greeting", "standalone_query": "hola", "reply": " ¡Hola! "}', "hola"
    )
    assert result == IntentResult(in_scope=True, reason="greeting", standalone_query="hola", small_talk=True, reply="¡Hola!")

    result = parse_classifier_output('{"in_scope": true, "small_talk": "yes", "reply": 3}', "q")
    assert result.small_talk is False and result.reply == ""
