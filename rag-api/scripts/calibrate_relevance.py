#!/usr/bin/env python3
"""
Calibrate RELEVANCE_THRESHOLD for the domain guardrail.

Prints the best COSINE similarity Milvus returns for sample in-scope and
out-of-scope questions, plus a suggested threshold halfway between both groups.

Usage (from rag-api/, with Milvus running):
    python -m scripts.calibrate_relevance
    python -m scripts.calibrate_relevance --file my_questions.json   # {"in_scope": [...], "out_of_scope": [...]}
"""

import argparse
import asyncio
import json

IN_SCOPE = [
    "¿Qué es la Paz Grande?",
    "¿Cuáles son las recomendaciones de la Comisión de la Verdad?",
    "¿Cómo afectó el conflicto armado a las comunidades indígenas?",
    "¿Qué papel tuvo el narcotráfico en el conflicto colombiano?",
    "¿Cuántas personas fueron desaparecidas forzadamente?",
    "What does the Truth Commission say about forced displacement?",
    "What were the main findings about paramilitary groups?",
    "How did the conflict affect women and girls?",
]

OUT_OF_SCOPE = [
    "Escríbeme un script en Python que ordene una lista",
    "¿Quién ganó el mundial de fútbol de 2022?",
    "Dame una receta de lasaña",
    "¿Cuál es la capital de Australia?",
    "Write a SQL query to join two tables",
    "Recommend me a good Netflix series",
    "What is the derivative of x squared?",
    "Tell me a joke",
]


async def best_score(question, embedding_service, vector_db, top_k):
    embedding = await embedding_service.generate_embedding(question)
    documents = await vector_db.search_similar_documents(embedding, top_k)
    return max((doc.score for doc in documents), default=0.0)


async def main(in_scope, out_of_scope):
    from src.infrastructure.config import config_service
    from src.infrastructure.dependencies import get_embedding_service, get_vector_database

    embedding_service = get_embedding_service()
    vector_db = get_vector_database()
    top_k = config_service.app.top_k

    results = {}
    for label, questions in (("in_scope", in_scope), ("out_of_scope", out_of_scope)):
        results[label] = [(q, await best_score(q, embedding_service, vector_db, top_k)) for q in questions]

    print("\n=== Best COSINE similarity per question ===")
    for label, rows in results.items():
        print(f"\n[{label}]")
        for question, score in sorted(rows, key=lambda row: row[1]):
            print(f"  {score:.4f}  {question}")

    lowest_in = min(score for _, score in results["in_scope"])
    highest_out = max(score for _, score in results["out_of_scope"])
    print(f"\nLowest in-scope score:      {lowest_in:.4f}")
    print(f"Highest out-of-scope score: {highest_out:.4f}")
    print(f"Current RELEVANCE_THRESHOLD: {config_service.guardrails.relevance_threshold}")
    if lowest_in > highest_out:
        print(f"Suggested RELEVANCE_THRESHOLD: {(lowest_in + highest_out) / 2:.2f}")
    else:
        print("Groups overlap: the intent classifier must carry the decision; "
              "pick a threshold just below the lowest in-scope score.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", help="JSON file with 'in_scope' and 'out_of_scope' question lists")
    args = parser.parse_args()

    in_scope, out_of_scope = IN_SCOPE, OUT_OF_SCOPE
    if args.file:
        with open(args.file, encoding="utf-8") as handle:
            data = json.load(handle)
        in_scope, out_of_scope = data["in_scope"], data["out_of_scope"]

    asyncio.run(main(in_scope, out_of_scope))
