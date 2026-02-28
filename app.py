import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

import streamlit as st

from rag_search import semantic_search, get_dsn
from ollama_client import ollama_one_sentence_answer_for_result, ollama_answer_from_context

load_dotenv()

st.set_page_config(
    page_title="Recherche sémantique (RAG) - Boulangerie & Pâtisserie",
    page_icon="🔎",
    layout="wide",
)

st.title("Recherche sémantique dans les fiches techniques ")
st.write(
    "Entrez une question en langage naturel. Le système renvoie les **3 fragments** les plus pertinents "
    "selon la **similarité cosinus** (embeddings all-MiniLM-L6-v2)."
)

with st.sidebar:
    st.subheader("Configuration")
    st.code(get_dsn(), language="text")

    st.subheader("Paramètres recherche")
    top_k = st.number_input("Top K", min_value=1, max_value=20, value=int(os.getenv("TOP_K", "3")), step=1)
    show_chars = st.slider("Affichage fragment (caractères)", min_value=200, max_value=4000, value=1200, step=100)

    st.subheader("LLM (Ollama)")
    use_ollama = st.checkbox("Activer LLM", value=True)
    ollama_model = st.selectbox("Modèle", ["phi3:mini", "mistral", "llama3.1"], index=0)
    ollama_timeout = st.number_input("Timeout (secondes)", min_value=10, max_value=180, value=60, step=5)

    st.subheader("Optimisation vitesse")
    max_chars_for_llm = st.number_input(
        "Texte envoyé au LLM (max chars / fragment)",
        min_value=300,
        max_value=2500,
        value=900,
        step=100,
    )
    st.caption("Conseil: phi3:mini + 700-900 chars => plus rapide.")

question = st.text_area(
    "Votre question",
    value="c'est quoi l'acide ascorbique ?",
    height=100,
)

col1, col2 = st.columns([1, 3])
with col1:
    run = st.button("Rechercher", type="primary")
with col2:
    st.caption("Astuce: soyez précis (ex: nom d’enzyme, dosage, ppm, % farine, etc.)")

# Session state init
if "results" not in st.session_state:
    st.session_state["results"] = []
if "summaries" not in st.session_state:
    st.session_state["summaries"] = {}  # index -> phrase
if "final_answer" not in st.session_state:
    st.session_state["final_answer"] = None
if "last_question" not in st.session_state:
    st.session_state["last_question"] = ""

# Retrieval
if run:
    q = question.strip()
    if not q:
        st.warning("Veuillez saisir une question.")
        st.stop()

    with st.spinner("Recherche des fragments les plus pertinents..."):
        try:
            st.session_state["results"] = semantic_search(q, top_k=int(top_k))
            st.session_state["summaries"] = {}
            st.session_state["final_answer"] = None
            st.session_state["last_question"] = q
        except Exception as e:
            st.error(f"Erreur: {e}")
            st.stop()

results = st.session_state["results"]
last_q = st.session_state["last_question"]

st.subheader("Résultats")
if not results:
    st.info("Lancez une recherche pour afficher les résultats.")
    st.stop()

# LLM actions
if use_ollama:
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Générer 1 phrase (réponse) par résultat", type="secondary"):
            with st.spinner("Ollama génère 1 phrase par fragment..."):
                phrases = {}

                with ThreadPoolExecutor(max_workers=min(3, len(results))) as ex:
                    futures = {}
                    for i, r in enumerate(results, start=1):
                        frag = (r.texte_fragment or "").strip().replace("\r", "")
                        frag = frag[: int(max_chars_for_llm)]

                        futures[
                            ex.submit(
                                ollama_one_sentence_answer_for_result,
                                last_q,
                                frag,
                                model=ollama_model,
                                timeout=int(ollama_timeout),
                                max_chars=int(max_chars_for_llm),
                            )
                        ] = i

                    for f in as_completed(futures):
                        i = futures[f]
                        try:
                            phrases[i] = f.result()
                        except Exception as e:
                            phrases[i] = f"(Erreur LLM: {e})"

                st.session_state["summaries"] = phrases

    with c2:
        if st.button("Générer une réponse finale (Top-K)", type="secondary"):
            contexts = [
                {"id_document": r.id_document, "score": r.score, "texte_fragment": r.texte_fragment}
                for r in results
            ]
            with st.spinner("Ollama génère une réponse à partir des fragments..."):
                try:
                    answer = ollama_answer_from_context(
                        question=last_q,
                        contexts=contexts,
                        model=ollama_model,
                        timeout=int(ollama_timeout),
                        max_chars_per_context=int(max_chars_for_llm),
                    )
                except Exception as e:
                    st.session_state["final_answer"] = f"(Erreur LLM: {e})"
                else:
                    st.session_state["final_answer"] = answer

# Display final answer
if use_ollama and st.session_state.get("final_answer"):
    st.divider()
    st.subheader("Réponse finale (LLM)")
    st.success(st.session_state["final_answer"])

# Display results
for i, r in enumerate(results, start=1):
    score_pct = r.score * 100
    text = (r.texte_fragment or "").strip().replace("\r", "")
    display_text = text
    if len(display_text) > show_chars:
        display_text = display_text[:show_chars].rstrip() + " ..."

    with st.container(border=True):
        st.markdown(f"### Résultat {i}")
        st.markdown(f"**Document:** `{r.id_document}`")
        st.markdown(f"**Score de similarité:** `{r.score:.4f}` ({score_pct:.1f}%)")
        st.markdown("**Texte du fragment :**")
        st.write(display_text)

        if use_ollama:
            phrase = st.session_state["summaries"].get(i)
            if phrase:
                st.markdown("**Phrase (LLM) :**")
                st.info(phrase)
            else:
                st.caption("Cliquez sur “Générer 1 phrase…” pour obtenir une phrase qui répond à la question.")