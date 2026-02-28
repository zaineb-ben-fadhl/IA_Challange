from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Tuple

import fitz  # pymupdf
import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings
from db import get_connection


def extract_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    doc.close()
    text = "\n".join(parts)
    # Nettoyage léger
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Chunking simple par longueur de caractères, avec overlap.
    (Suffisant pour prototype. Peut être amélioré par chunking par paragraphes.)
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def to_pgvector_literal(vec: np.ndarray) -> str:
    vec_list = vec.astype(float).tolist()
    return "[" + ",".join(f"{x:.8f}" for x in vec_list) + "]"


def ensure_schema():
    schema_path = Path("schema.sql")
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def ingest_folder(pdf_folder: Path):
    """
    Ingestion:
    - pour chaque PDF => id_document incremental
    - extraction texte -> chunks
    - embedding de chaque chunk (normalisé) avec all-MiniLM-L6-v2
    - insertion dans embeddings(id_document, texte_fragment, vecteur)
    """
    ensure_schema()

    model = SentenceTransformer(settings.embedding_model)
    test_vec = model.encode("test", normalize_embeddings=True)
    if len(test_vec) != 384:
        raise ValueError(f"Le modèle n'est pas en 384 dimensions: {len(test_vec)}")

    pdf_files = sorted([p for p in pdf_folder.rglob("*.pdf")])
    if not pdf_files:
        raise RuntimeError(f"Aucun PDF trouvé dans: {pdf_folder}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            doc_id = 1
            for pdf in pdf_files:
                text = extract_text_from_pdf(pdf)
                chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
                if not chunks:
                    print(f"[SKIP] {pdf.name}: texte vide")
                    doc_id += 1
                    continue

                embeddings = model.encode(chunks, normalize_embeddings=True)
                # Insert chunk par chunk
                for chunk, emb in zip(chunks, embeddings):
                    emb = np.array(emb, dtype=np.float32)
                    vec_literal = to_pgvector_literal(emb)

                    cur.execute(
                        """
                        INSERT INTO embeddings (id_document, texte_fragment, vecteur)
                        VALUES (%s, %s, %s::vector)
                        """,
                        (doc_id, chunk, vec_literal),
                    )

                print(f"[OK] {pdf.name}: {len(chunks)} fragments insérés (id_document={doc_id})")
                doc_id += 1

        conn.commit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest PDFs into PostgreSQL (pgvector).")
    parser.add_argument(
        "--pdf_dir",
        required=True,
        help="Chemin du dossier contenant les PDF (ex: ./embedding)",
    )
    args = parser.parse_args()

    ingest_folder(Path(args.pdf_dir))