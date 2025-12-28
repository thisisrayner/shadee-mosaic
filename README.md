# Shadee Mosaic: Internal Brain Explorer 🧠

A high-fidelity semantic search engine for exploratory clinical narrative analysis. This tool allows non-technical stakeholders to query the "Internal Brain" (PostgreSQL + pgvector) using natural language to find anonymized narratives and AI classifications.

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- **Python 3.9+**
- **Supabase Account** with the `social_posts` table.
- **Gemini API Key** (for generating embeddings).

### 2. Database Preparation
Before running the explorer, the database function must support rich metadata retrieval:
1. Go to your **Supabase SQL Editor**.
2. Run the code found in `scripts/phase2_schema_update.sql`.
   - *Note: If you get a warning about "destructive operation", it is safe to proceed (we are upgrading the search return type).*

### 3. Local Environment Setup
```powershell
# 1. Activate your virtual environment
& ".venv/Scripts/Activate.ps1"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your .env
# Ensure SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and GEMINI_API_KEY are set.
```

### 4. Spin up the Internal Brain
```powershell
python src/ai/app.py
```
Visit **[http://localhost:8000](http://localhost:8000)** to start exploring.

---

## ✨ Key Features
- **Semantic Narrative Search:** Search by "vibes" or themes (e.g. "academic stress") instead of just keywords.
- **PII Shadow Strategy:** Displays high-fidelity anonymized narratives (`content_scrubbed`) for safety.
- **Deep-Dive Modal:** Click any result to see the original content, AI Bucket classification, and the AI's detailed explanation for the flagging.
- **Glassmorphism UI:** A premium, high-performance web interface designed for stakeholder presentations.

## 📂 Project Structure
- `src/ai/app.py`: FastAPI backend and API layer.
- `src/ai/static/index.html`: Vanilla JS/CSS frontend with Glassmorphism design.
- `src/ai/search.py`: Core RAG retrieval logic using Gemini embeddings.
- `scripts/phase2_schema_update.sql`: Database migration for vector-search and metadata support.

---

## 🛠️ Diagnostics
If you encounter issues, visit:
`http://localhost:8000/api/debug-db`
This will check if your Supabase function signature matches the expected frontend metadata.
