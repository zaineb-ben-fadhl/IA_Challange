export type SearchResult = {
  id_document: number | string;
  score: number; // 0..1
  texte_fragment: string;
  phrase_llm?: string;
};

export type SearchResponse = {
  question: string;
  top_k: number;
  results: SearchResult[];
  final_answer?: string | null;
};

export type SearchRequest = {
  question: string;
  top_k: number;
  max_chars_for_llm: number;
  use_ollama: boolean;
  model: string;
  timeout: number;
  mode: "none" | "per_result" | "final"; // quel type de génération
};