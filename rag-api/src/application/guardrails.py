"""Domain relevance guardrail: intent classification + vector store relevance threshold."""

from typing import List, Dict, Any, Optional, Protocol

from ..domain.entities import ScopeDecision
from ..domain.ports import QueryGuardrail, EmbeddingService, VectorDatabase


OUT_OF_SCOPE_MESSAGES = {
    "es": (
        "Solo puedo responder preguntas relacionadas con el Informe de la Comisión de la Verdad "
        "y los documentos indexados en este proyecto. Por favor realiza una pregunta afín al tema."
    ),
    "en": (
        "I can only answer questions related to the Truth Commission Report and the indexed "
        "documents in this project. Please ask a topic-relevant question."
    ),
}


def out_of_scope_message(language: str) -> str:
    """Return the standard rejection message for the requested language."""
    return OUT_OF_SCOPE_MESSAGES.get(language, OUT_OF_SCOPE_MESSAGES["es"])


SMALL_TALK_MESSAGES = {
    "es": (
        "¡Hola! Soy Ventana a la Verdad, un asistente sobre el Informe Final de la Comisión de la Verdad. "
        "¿Qué te gustaría saber sobre el conflicto armado, las víctimas o las recomendaciones del Informe?"
    ),
    "en": (
        "Hi! I'm Window to Truth, an assistant about the Final Report of the Truth Commission. "
        "What would you like to know about the armed conflict, the victims or the Report's recommendations?"
    ),
}


def small_talk_message(language: str) -> str:
    """Return the default small talk reply for the requested language."""
    return SMALL_TALK_MESSAGES.get(language, SMALL_TALK_MESSAGES["es"])


class IntentClassifier(Protocol):
    """Anything that can classify a question; returns None when unavailable."""

    async def classify(self, question: str, chat_history: List[Dict[str, Any]]):
        ...


class DomainGuardrail(QueryGuardrail):
    """
    Two-layer guardrail evaluated before retrieval-augmented generation:
      1. Intent classifier rejects clearly off-topic requests (code, entertainment, ...).
      2. The best COSINE similarity in Milvus must reach the relevance threshold;
         otherwise the indexed documents cannot support an answer.
    If the classifier fails, the threshold alone decides (fail-open to layer 2).
    """

    def __init__(
        self,
        classifier: Optional[IntentClassifier],
        embedding_service: EmbeddingService,
        vector_db: VectorDatabase,
        relevance_threshold: float,
        top_k: int = 5
    ):
        self._classifier = classifier
        self._embedding_service = embedding_service
        self._vector_db = vector_db
        self._relevance_threshold = relevance_threshold
        self._top_k = top_k

    async def evaluate(
        self,
        question: str,
        chat_history: List[Dict[str, Any]],
        language: str = "es"
    ) -> ScopeDecision:
        standalone_query = question

        if self._classifier is not None:
            intent = await self._classifier.classify(question, chat_history)
            if intent is not None:
                if not intent.in_scope:
                    print(f"Guardrail: rejected by intent classifier ({intent.reason})")
                    return ScopeDecision(in_scope=False, reason="intent", standalone_query=intent.standalone_query)
                if intent.small_talk:
                    # Greetings, thanks, "what can you do?": answer directly, they never pass the threshold
                    return ScopeDecision(
                        in_scope=True,
                        reason="small_talk",
                        standalone_query=intent.standalone_query,
                        reply=intent.reply or small_talk_message(language)
                    )
                standalone_query = intent.standalone_query

        embedding = await self._embedding_service.generate_embedding(standalone_query)
        documents = await self._vector_db.search_similar_documents(embedding, self._top_k)
        max_score = max((doc.score for doc in documents), default=None)

        if max_score is None or max_score < self._relevance_threshold:
            print(f"Guardrail: rejected by relevance threshold (max_score={max_score}, threshold={self._relevance_threshold})")
            return ScopeDecision(
                in_scope=False,
                reason="low_relevance",
                standalone_query=standalone_query,
                max_score=max_score
            )

        return ScopeDecision(in_scope=True, reason="ok", standalone_query=standalone_query, max_score=max_score)
