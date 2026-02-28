from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


@dataclass(frozen=True)
class SearchResult:
    id_document: int
    texte_fragment: str
    score: float


def _to_pgvector_literal(vec: np.ndarray) -> str:
    vec_list = vec.astype(float).tolist()
    return "[" + ",".join(f"{x:.8f}" for x in vec_list) + "]"


def get_dsn() -> str:
    load_dotenv()
    host = os.getenv("PG_HOST", "127.0.0.1")
    port = os.getenv("PG_PORT", "5433")
    db = os.getenv("PG_DB", "rag_db")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    # cache simple en mémoire (évite de re-télécharger/recharger à chaque clic)
    global _model
    if _model is None:
        load_dotenv()
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model


def semantic_search(question: str, top_k: int = 3) -> List[SearchResult]:
    load_dotenv()
    model = get_model()

    q_vec = model.encode(question, normalize_embeddings=True)
    if len(q_vec) != 384:
        raise ValueError(f"Dimension embedding invalide: {len(q_vec)} (attendu 384)")

    vec_literal = _to_pgvector_literal(np.array(q_vec, dtype=np.float32))
    dsn = get_dsn()

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  id_document,
                  texte_fragment,
                  1 - (vecteur <=> %s::vector) AS score
                FROM embeddings
                ORDER BY vecteur <=> %s::vector
                LIMIT %s;
                """,
                (vec_literal, vec_literal, top_k),
            )
            rows = cur.fetchall()

    return [
        SearchResult(
            id_document=int(r[0]),
            texte_fragment=str(r[1]),
            score=float(r[2]),
        )
        for r in rows
    ]