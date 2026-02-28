# Rose Blanche Group — Recherche sémantique (pgvector) + Frontend React (Vite) + API FastAPI (+ Ollama)

Ce projet fournit une application complète de **recherche sémantique** sur des fiches techniques (ou documents PDF découpés en fragments) :

- **Backend** : PostgreSQL + **pgvector** + embeddings (**all-MiniLM-L6-v2**) + (optionnel) **Ollama** pour générer des phrases/réponses.
- **Frontend** : **React + TypeScript + Vite** avec un thème basé sur le logo **Rose Blanche Group** (bordeaux + or/blé).

---

## Démo vidéo

- **Video Demo (Google Drive)** : https://drive.google.com/file/d/15AhBHO6ST0r1cYKf0zv2JZYru2flfaNT/view?usp=sharing

> Remarque : GitHub ne peut pas intégrer directement une vidéo Google Drive en lecture “embed”. Le lien ouvre la vidéo sur Drive.

---

## Fonctionnalités

### Recherche (RAG / vector search)
- Entrée : une question en langage naturel.
- Calcul : embedding de la question (`all-MiniLM-L6-v2`, 384 dimensions).
- Recherche : **Top‑K fragments** les plus proches via **similarité cosinus** (pgvector).
- Affichage : score + document + texte du fragment (nettoyé et plus lisible côté UI).

### LLM (optionnel via Ollama)
Deux actions (comme dans votre version Streamlit) :
- **Générer 1 phrase par résultat** (utilise uniquement le fragment)
- **Générer une réponse finale (Top‑K)** (synthèse depuis les Top‑K fragments)

---

## Architecture (recommandée)

```
Defi/
├─ backend/
│  ├─ api.py
│  ├─ requirements.txt
│  ├─ __init__.py
│  ├─ rag_search.py
│  └─ ollama_client.py
└─ warda-bida-frontend/
   ├─ src/
   ├─ package.json
   └─ ...
```

---

## Prérequis

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** + extension **pgvector**
- (Optionnel) **Ollama** : https://ollama.com

---

## Base de données (pgvector)

### 1) Activer pgvector
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2) Table `embeddings` (structure attendue)
La table doit contenir :
- `id` (PK)
- `id_document` (int)
- `texte_fragment` (text)
- `vecteur` (vector(384))

Exemple :
```sql
CREATE TABLE IF NOT EXISTS embeddings (
  id SERIAL PRIMARY KEY,
  id_document INTEGER NOT NULL,
  texte_fragment TEXT NOT NULL,
  vecteur vector(384) NOT NULL
);
```

> Important : `vector(384)` correspond au modèle `all-MiniLM-L6-v2`.

---

## Backend (FastAPI)

### Installation
```powershell
cd backend
pip install -r requirements.txt
```

### Lancer l’API
```powershell
cd C:\Users\DELL\Desktop\Defi
uvicorn backend.api:app --reload --port 8000
```

### Endpoints utiles
- `GET /health` → status OK
- `POST /search` → recherche + (optionnel) génération LLM

Swagger UI :
- http://127.0.0.1:8000/docs

---

## Frontend (React + TypeScript + Vite)

### Installation
```powershell
cd warda-bida-frontend
npm install
```

### Configuration API
Créez un fichier `.env` dans `warda-bida-frontend/` :

```dotenv
VITE_API_URL=http://127.0.0.1:8000/search
```

> Redémarrez `npm run dev` après toute modification du `.env`.

### Lancer le frontend
```powershell
npm run dev
```

Ouvrir :
- http://localhost:5173

---

## Utilisation

1. Saisir une question (ex : **"c'est quoi l'acide ascorbique ?"**)
2. Choisir `Top K`
3. Cliquer **Rechercher**
4. (Optionnel) Dans le panneau **LLM (Ollama)** :
   - **Générer 1 phrase / résultat**
   - **Générer réponse finale (Top‑K)**

---

## Ollama (optionnel)

### Installer un modèle rapide (recommandé)
```powershell
ollama pull phi3:mini
```

### Vérifier l’API Ollama
```powershell
curl http://localhost:11434/api/tags
```

---

## Notes / Limitations

- Les PDF peuvent contenir des retours ligne et puces “spéciales”. Le frontend applique un nettoyage pour rendre le texte plus lisible.
- Certains fragments peuvent commencer au milieu d’un mot (“Types…” → “ypes…”) si le découpage des fragments n’a pas d’overlap.  
  Amélioration possible : **chunk overlap** + nettoyage PDF avant embeddings.

---

## Commandes utiles

### Backend
```powershell
uvicorn backend.api:app --reload --port 8000
```

### Frontend
```powershell
npm run dev
```

---

## Auteur
- GitHub : zaineb-ben-fadhl
- Date : 2026-02-28