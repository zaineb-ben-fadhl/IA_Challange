# Recherche sémantique (pgvector) + Frontend Streamlit (+ Bonus LLM Ollama)
## Démo vidéo

## Démo vidéo

[Voir la vidéo](https://drive.google.com/file/d/1fi5-Qb_iu9Z19ZndmqJonro9G4b9gaPj/view?usp=sharing)

> Remarque : sur GitHub, le lien ouvre la vidéo dans un nouvel onglet (selon le navigateur). GitHub ne permet pas de forcer `target="_blank"` dans un README.


Ce projet implémente un **module de recherche sémantique** sur une base vectorielle PostgreSQL/**pgvector** et une interface **Streamlit**.
Le système :
- reçoit une question utilisateur,
- génère son embedding (**all-MiniLM-L6-v2**, dimension 384),
- calcule la similarité cosinus avec les embeddings stockés en base,
- retourne les **Top K** fragments (par défaut **3**) avec leur **score**.

Un **LLM local (Ollama)** peut :
- générer **une phrase** qui répond à la question pour **chaque fragment**, ou
- générer une **réponse finale** synthétique à partir des Top‑K fragments.

---

## Démo vidéo

- **Video Demo (Google Drive)** : https://drive.google.com/file/d/15AhBHO6ST0r1cYKf0zv2JZYru2flfaNT/view?usp=sharing

> Remarque: GitHub ne peut pas “embed” directement une vidéo Google Drive en lecture intégrée.
> Le lien ci-dessus ouvre la vidéo dans Google Drive.

---

## Prérequis

- **Python 3.10+**
- **PostgreSQL** + extension **pgvector**
- Windows / Linux / macOS
- **Ollama** pour le résumé LLM : https://ollama.com

---

## Structure du projet (exemple)

- `app.py` : application Streamlit (frontend)
- `rag_search.py` : module de recherche sémantique (embedding + requêtes pgvector)
- `ollama_client.py` : client Ollama (résumé/answer)
- `search.py` : (optionnel) version CLI de la recherche
- `.env` : variables d’environnement (non commité)
- `requirements.txt` : dépendances Python

---

## Installation

### 1) Créer et activer un environnement virtuel

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Installer les dépendances

```powershell
pip install -U pip
pip install -r requirements.txt
```

---

## Configuration (.env)

Créez un fichier `.env` à la racine du projet :

```dotenv
# PostgreSQL / pgvector
PG_HOST=127.0.0.1
PG_PORT=5433
PG_DB=rag_db
PG_USER=postgres
PG_PASSWORD=postgres

# Modèle d'embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Paramètres UI (optionnel)
TOP_K=3
```

---

## Base de données (pgvector)

### 1) Activer l’extension pgvector
Dans PostgreSQL :

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

---

## Lancer l’application Streamlit

```powershell
streamlit run app.py
```

Puis ouvrir l’URL affichée (souvent : http://localhost:8501).

---

## Utilisation (consigne)

1. Saisir une question (ex : **"Quel dosage est conseillé pour un blocage froid positif (2°C) ?"**)
2. Cliquer sur **Rechercher**
3. L’application affiche :
   - les **3 fragments** les plus pertinents (Top‑K),
   - le **score** de similarité cosinus,
   - le texte du fragment.

---

## Bonus : Résumé / réponse avec Ollama (LLM local)

### 1) Installer Ollama
Téléchargement : https://ollama.com

### 2) Télécharger un modèle léger (recommandé)
```powershell
ollama pull phi3:mini
```

### 3) Vérifier que l’API Ollama tourne
```powershell
curl http://localhost:11434/api/tags
```

### 4) Dans l’interface Streamlit
- Activez **"Activer LLM"**
- Cliquez sur :
  - **"Générer 1 phrase (réponse) par résultat"** (une phrase par fragment), ou
  - **"Générer une réponse finale (Top-K)"** (réponse synthétique à partir des Top‑K fragments).

> Astuce performance : gardez `phi3:mini` + 700–900 caractères max envoyés au LLM.

---

## Validation rapide (vérifier que E300/ascorbique est bien ingéré)

Dans PowerShell, vous pouvez tester si des fragments contiennent "ascorb" :

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); import psycopg; dsn=f\"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}\"; conn=psycopg.connect(dsn); cur=conn.cursor(); cur.execute(\"SELECT COUNT(*) FROM embeddings WHERE lower(texte_fragment) LIKE '%ascorb%';\"); print('fragments contenant ascorb* =', cur.fetchone()[0]); conn.close()"
```

---

## Notes / limitations

- La recherche vectorielle retourne les fragments les plus proches sémantiquement.
- Si une question demande **plusieurs ingrédients** (ex : amylase + xylanase + E300), il est possible que la base ne contienne pas un fragment unique avec les 3 informations. Dans ce cas :
  - le Top‑K peut contenir des fragments “séparés”,
  - la réponse doit être synthétisée à partir de plusieurs sources (le mode “réponse finale LLM” aide).

---

## Commandes utiles

- Lancer Streamlit :
```powershell
streamlit run app.py
```

- Voir les modèles Ollama installés :
```powershell
ollama list
```

- Tester Ollama :
```powershell
ollama run phi3:mini "Résume en une phrase: l'acide ascorbique (E300) en boulangerie."
```

---

## Auteur
- GitHub : zaineb-ben-fadhl
- Date : 2026-02-28