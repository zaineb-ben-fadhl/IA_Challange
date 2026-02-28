import type { SearchResult } from "../types";

function clampScore(score: number) {
  const s = Math.max(0, Math.min(1, score));
  return {
    value: s,
    pct: Math.round(s * 1000) / 10
  };
}

export function ResultCard({ result, index }: { result: SearchResult; index: number }) {
  const { value, pct } = clampScore(result.score);

  return (
    <article className="wb-card" style={{ animationDelay: `${index * 60}ms` }}>
      <header className="wb-card__head">
        <div className="wb-card__title">
          <span className="wb-badge">Résultat {index + 1}</span>
          <span className="wb-doc">Doc: {String(result.document)}</span>
        </div>

        <div className="wb-score" title="Score de similarité">
          <div className="wb-score__ring" aria-hidden="true">
            <div className="wb-score__fill" style={{ transform: `scaleX(${value})` }} />
          </div>
          <div className="wb-score__text">{pct}%</div>
        </div>
      </header>

      <div className="wb-card__body">
        <div className="wb-card__label">Fragment</div>
        <p className="wb-card__text">{result.text}</p>

        {result.llm_phrase ? (
          <div className="wb-llm">
            <div className="wb-card__label">Phrase (LLM)</div>
            <p className="wb-llm__text">{result.llm_phrase}</p>
          </div>
        ) : null}
      </div>
    </article>
  );
}