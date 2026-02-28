import { useState, useMemo } from "react";
import wardaLogo from "./assets/warda.png";
import { search } from "./api";
import type { SearchResponse } from "./types";
import { cleanFragmentText } from "./text";

function clamp(n: number, a: number, b: number) {
  return Math.max(a, Math.min(b, n));
}

function ScoreBar({ score }: { score: number }) {
  const pct = clamp(score, 0, 1) * 100;
  return (
    <div className="score">
      <div className="score__bar">
        <div className="score__fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="score__txt">{pct.toFixed(1)}%</div>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("c'est quoi l'acide ascorbique ?");
  const [topK, setTopK] = useState(3);
  const [showChars, setShowChars] = useState(1200);

  const [useOllama, setUseOllama] = useState(true);
  const [model, setModel] = useState("phi3:mini");
  const [timeout, setTimeoutSec] = useState(60);
  const [maxCharsLLM, setMaxCharsLLM] = useState(900);

  // Data state
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [data, setData] = useState<SearchResponse | null>(null);

  // LLM UI state (2 buttons)
  const [llmMode, setLlmMode] = useState<"none" | "per_result" | "final">("none");

  const subtitle = useMemo(
    () => "Recherche sémantique (pgvector) — Top‑K fragments + score cosinus — Option LLM (Ollama).",
    []
  );

  async function runSearch(mode: "none" | "per_result" | "final") {
    const q = question.trim();
    if (!q) return;

    setLoading(true);
    setErr(null);
    setLlmMode(mode);

    try {
      const res = await search({
        question: q,
        top_k: topK,
        max_chars_for_llm: maxCharsLLM,
        use_ollama: useOllama,
        model,
        timeout,
        mode: useOllama ? mode : "none"
      });
      setData(res);
    } catch (e: any) {
      setErr(e?.message ?? "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="bg" aria-hidden="true">
        <div className="orb orb--gold" />
        <div className="orb orb--pink" />
        <div className="sparkles" />
      </div>

      <header className="header">
        <div className="brand">
          <div className="brand__logo">
            <img src={wardaLogo} alt="Rose Blanche Group logo" />
          </div>
          <div className="brand__txt">
            <div className="brand__name">Recherche sémantique</div>
            <div className="brand__sub">{subtitle}</div>
          </div>
        </div>

        <div className="chips">
          <span className="chip">pgvector</span>
          <span className="chip">cosine similarity</span>
          <span className="chip">all‑MiniLM‑L6‑v2</span>
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="panel panel--glass">
            <div className="panel__head">
              <h1>Recherche sémantique dans les fiches techniques</h1>
              <p>
                Entrez une question en langage naturel. Le système renvoie les <b>Top‑K</b> fragments selon la{" "}
                <b>similarité cosinus</b>.
              </p>
            </div>

            <div className="form">
              <label className="label">Votre question</label>
              <textarea className="textarea" value={question} onChange={(e) => setQuestion(e.target.value)} rows={3} />

              <div className="row">
                <div className="field">
                  <div className="field__label">Top K</div>
                  <input
                    className="input"
                    type="number"
                    min={1}
                    max={20}
                    value={topK}
                    onChange={(e) => setTopK(clamp(Number(e.target.value || 3), 1, 20))}
                  />
                </div>

                <div className="field">
                  <div className="field__label">Afficher (chars)</div>
                  <input
                    className="input"
                    type="number"
                    min={200}
                    max={4000}
                    value={showChars}
                    onChange={(e) => setShowChars(clamp(Number(e.target.value || 1200), 200, 4000))}
                  />
                </div>

                <button className="btn" onClick={() => runSearch("none")} disabled={loading}>
                  {loading && llmMode === "none" ? (
                    <span className="btn__load">
                      <span className="spinner" /> Recherche…
                    </span>
                  ) : (
                    "Rechercher"
                  )}
                </button>
              </div>

              <div className="hint">Astuce: soyez précis (enzyme, dosage, ppm, % farine, température, etc.)</div>

              {err ? <div className="alert">{err}</div> : null}
            </div>
          </div>

          <aside className="panel panel--side">
            <div className="side__title">LLM (Ollama)</div>

            <div className="toggle">
              <input id="ollama" type="checkbox" checked={useOllama} onChange={(e) => setUseOllama(e.target.checked)} />
              <label htmlFor="ollama">Activer LLM</label>
            </div>

            <div className="grid2">
              <div className="field">
                <div className="field__label">Modèle</div>
                <select className="input" value={model} onChange={(e) => setModel(e.target.value)} disabled={!useOllama}>
                  <option value="phi3:mini">phi3:mini (rapide)</option>
                  <option value="mistral">mistral</option>
                  <option value="llama3.1">llama3.1</option>
                </select>
              </div>

              <div className="field">
                <div className="field__label">Timeout (s)</div>
                <input
                  className="input"
                  type="number"
                  value={timeout}
                  min={10}
                  max={180}
                  onChange={(e) => setTimeoutSec(clamp(Number(e.target.value || 60), 10, 180))}
                  disabled={!useOllama}
                />
              </div>

              <div className="field">
                <div className="field__label">Max chars / fragment</div>
                <input
                  className="input"
                  type="number"
                  value={maxCharsLLM}
                  min={300}
                  max={2500}
                  onChange={(e) => setMaxCharsLLM(clamp(Number(e.target.value || 900), 300, 2500))}
                  disabled={!useOllama}
                />
              </div>
            </div>

            <div className="side__note">
              Deux boutons comme Streamlit :
              <br />
              - 1 phrase / résultat
              <br />- Réponse finale Top‑K
            </div>

            <div className="llmBtns">
              <button className="btn btn--secondary" onClick={() => runSearch("per_result")} disabled={loading || !useOllama}>
                {loading && llmMode === "per_result" ? (
                  <span className="btn__load">
                    <span className="spinner spinner--dark" /> Génération…
                  </span>
                ) : (
                  "Générer 1 phrase / résultat"
                )}
              </button>

              <button className="btn btn--secondary" onClick={() => runSearch("final")} disabled={loading || !useOllama}>
                {loading && llmMode === "final" ? (
                  <span className="btn__load">
                    <span className="spinner spinner--dark" /> Génération…
                  </span>
                ) : (
                  "Générer réponse finale (Top‑K)"
                )}
              </button>
            </div>
          </aside>
        </section>

        {data?.final_answer ? (
          <section className="panel panel--glass final">
            <div className="final__title">Réponse finale (LLM)</div>
            <div className="final__text">{data.final_answer}</div>
          </section>
        ) : null}

        <section className="results">
          <div className="results__head">
            <h2>Résultats</h2>
            <div className="results__meta">{data?.results?.length ? `${data.results.length} fragment(s)` : "—"}</div>
          </div>

          <div className="cards">
            {(data?.results ?? []).map((r, idx) => {
              const cleaned = cleanFragmentText(r.texte_fragment || "");
              const show = cleaned.slice(0, showChars);
              const needsDots = cleaned.length > showChars;

              return (
                <article key={`${r.id_document}-${idx}`} className="card">
                  <div className="card__top">
                    <div className="badge">Résultat {idx + 1}</div>
                    <div className="doc">Document: {String(r.id_document)}</div>
                  </div>

                  <div className="card__score">
                    <ScoreBar score={r.score} />
                  </div>

                  <div className="card__label">Texte du fragment</div>
                  <div className="card__text">
                    {show}
                    {needsDots ? " …" : ""}
                  </div>

                  {r.phrase_llm ? (
                    <>
                      <div className="card__label">Phrase (LLM)</div>
                      <div className="llm">{r.phrase_llm}</div>
                    </>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>

        <footer className="footer">
          <div>© {new Date().getFullYear()} Rose Blanche Group</div>
          <div className="footer__muted">React UI • FastAPI • pgvector • Ollama</div>
        </footer>
      </main>
    </div>
  );
}