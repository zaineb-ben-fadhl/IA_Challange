CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
  id SERIAL PRIMARY KEY,
  id_document INT NOT NULL,
  texte_fragment TEXT NOT NULL,
  vecteur VECTOR(384) NOT NULL
);

-- Index recommandé (rapide) si supporté par votre version pgvector
CREATE INDEX IF NOT EXISTS embeddings_vecteur_hnsw
ON embeddings
USING hnsw (vecteur vector_cosine_ops);