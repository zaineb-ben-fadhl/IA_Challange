import type { SearchRequest, SearchResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/search";

export async function search(req: SearchRequest): Promise<SearchResponse> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req)
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`API error ${res.status}: ${txt}`);
  }

  return (await res.json()) as SearchResponse;
}