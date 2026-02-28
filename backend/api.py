from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_search import semantic_search
from ollama_client import (
    ollama_one_sentence_answer_for_result,
    ollama_answer_from_context,
)


# ----------------------------
# Pydantic models (API schema)
# ----------------------------
class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question utilisateur")
    top_k: int = Field(3, ge=1, le=20, description="Nombre de fragments à retourner (Top-K)")

    # LLM options (Ollama)
    use_ollama: bool = Field(True, description="Active/désactive l'appel LLM")
    mode: Literal["none", "per_result", "final"] = Field(
        "per_result",
        description="none: pas de LLM; per_result: 1 phrase par fragment; final: réponse finale depuis Top-K",
    )
    model: str = Field("phi3:mini", description="Nom du modèle Ollama (ex: phi3:mini)")
    timeout: int = Field(60, ge=10, le=180, description="Timeout HTTP (secondes) pour Ollama")
    max_chars_for_llm: int = Field(900, ge=300, le=2500, description="Texte max envoyé au LLM par fragment")


class SearchResult(BaseModel):
    id_document: Any
    score: float
    texte_fragment: str
    phrase_llm: Optional[str] = None


class SearchResponse(BaseModel):
    question: str
    top_k: int
    results: List[SearchResult]
    final_answer: Optional[str] = None


# ----------------------------
# App + CORS
# ----------------------------
app = FastAPI(title="Warda Search API", version="1.0.0")

# Autoriser React (Vite) à appeler l’API en dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Helpers
# ----------------------------
def _to_dict(r: Any) -> Dict[str, Any]:
    """
    Convertit un résultat (dataclass / pydantic / dict) en dict.
    Votre semantic_search retourne souvent une dataclass, d'où ce helper.
    """
    if is_dataclass(r):
        return asdict(r)
    if hasattr(r, "dict"):
        return r.dict()  # type: ignore[attr-defined]
    return dict(r)


# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Warda API is running. Use GET /health and POST /search."}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    # 1) Retrieval (pgvector)
    results_raw = semantic_search(req.question, top_k=req.top_k)

    results: List[SearchResult] = []
    for r in results_raw:
        d = _to_dict(r)
        results.append(
            SearchResult(
                id_document=d.get("id_document"),
                score=float(d.get("score", 0.0)),
                texte_fragment=str(d.get("texte_fragment") or ""),
                phrase_llm=None,
            )
        )

    final_answer: Optional[str] = None

    # 2) Generation (Ollama) optionnelle
    if req.use_ollama and req.mode != "none":
        if req.mode == "per_result":
            for i in range(len(results)):
                frag = results[i].texte_fragment[: req.max_chars_for_llm]
                results[i].phrase_llm = ollama_one_sentence_answer_for_result(
                    question=req.question,
                    fragment=frag,
                    model=req.model,
                    timeout=req.timeout,
                    max_chars=req.max_chars_for_llm,
                )

        elif req.mode == "final":
            contexts = [
                {"id_document": r.id_document, "score": r.score, "texte_fragment": r.texte_fragment}
                for r in results
            ]
            final_answer = ollama_answer_from_context(
                question=req.question,
                contexts=contexts,
                model=req.model,
                timeout=req.timeout,
                max_chars_per_context=req.max_chars_for_llm,
            )

    return SearchResponse(
        question=req.question,
        top_k=req.top_k,
        results=results,
        final_answer=final_answer,
    )