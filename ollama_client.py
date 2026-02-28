from __future__ import annotations

import json
import urllib.request
from typing import List, Dict


def _ollama_generate(
    prompt: str,
    model: str = "phi3:mini",
    base_url: str = "http://localhost:11434",
    timeout: int = 60,
    num_predict: int = 120,
    temperature: float = 0.2,
) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }

    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return (data.get("response") or "").strip()


def ollama_one_sentence_answer_for_result(
    question: str,
    fragment: str,
    model: str = "phi3:mini",
    base_url: str = "http://localhost:11434",
    timeout: int = 60,
    max_chars: int = 900,
) -> str:
    """
    Génère UNE phrase qui répond à la question en utilisant UNIQUEMENT le fragment.
    Si le fragment ne contient pas l'info => "Non indiqué dans ce fragment."
    """
    frag = (fragment or "").strip().replace("\r", "")
    if len(frag) > max_chars:
        frag = frag[:max_chars].rstrip() + " ..."

    prompt = f"""Tu es un assistant.
Ta tâche: produire UNE seule phrase qui répond à la question en utilisant UNIQUEMENT le fragment.

Question: {question}

Fragment:
{frag}

Règles:
- 1 seule phrase en français, complète (pas coupée).
- Garde les chiffres/dosages/unités s'ils existent.
- Ne rajoute pas d'informations externes.
- Si le fragment ne contient pas la réponse, écris exactement: "Non indiqué dans ce fragment."

Phrase:"""

    return _ollama_generate(
        prompt=prompt,
        model=model,
        base_url=base_url,
        timeout=timeout,
        num_predict=90,
        temperature=0.1,
    )


def ollama_answer_from_context(
    question: str,
    contexts: List[Dict],
    model: str = "phi3:mini",
    base_url: str = "http://localhost:11434",
    timeout: int = 60,
    max_chars_per_context: int = 900,
) -> str:
    """
    Génère une réponse finale (1-2 phrases) en se basant UNIQUEMENT sur les Top-K fragments.
    """
    sources_txt = []
    for i, c in enumerate(contexts, start=1):
        frag = (c.get("texte_fragment") or "").strip().replace("\r", "")
        if len(frag) > max_chars_per_context:
            frag = frag[:max_chars_per_context].rstrip() + " ..."

        sources_txt.append(
            f"[Source {i}] doc={c.get('id_document')} score={float(c.get('score', 0.0)):.4f}\n{frag}"
        )

    joined_sources = "\n\n".join(sources_txt)

    prompt = f"""Tu es un assistant expert en boulangerie/pâtisserie.
Réponds à la question UNIQUEMENT à partir des sources.
Si l'information n'est pas présente, dis: "Je ne trouve pas l'information dans les documents fournis."

Question:
{question}

Sources:
{joined_sources}

Consignes:
- Réponse courte (1 à 2 phrases).
- Garde les chiffres et unités (ppm, %, g/tonne).
- Si plusieurs ingrédients sont demandés, répond par ingrédient SI l’info existe dans les sources.
- Termine par: Sources utilisées: 1,2,3 (uniquement celles réellement utilisées).

Réponse:"""

    return _ollama_generate(
        prompt=prompt,
        model=model,
        base_url=base_url,
        timeout=timeout,
        num_predict=160,
        temperature=0.2,
    )