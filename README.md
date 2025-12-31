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
- **Dynamic Research Engine (Phase 3/4):** Recursive sampling (N=25 -> N=120 -> N=500) with AI-led thematic saturation audits.
- **Protocol Trace (Clinical Transparency):** A dedicated Git-style log tab providing 100% visibility into backend research protocols, semantic thresholds, and JSON reasoning.
- **Gemini 3.0 Integration:** Final synthesis powered by `gemini-3-flash-preview` for high-fidelity clinical reasoning.
- **Research Query Logging:** Automatic tracking of all user questions and AI responses in a structured `research_logs` table for analytical lineage.
- **Atmosphere Pulse:** Real-time Google Trends visualization for mental health keywords (Anxiety, Depression, etc.).
- **Semantic Narrative Search:** Search by "vibes" or themes instead of just keywords.
- **Deep-Dive Modal:** Clinical triage view with original content (if requested), AI Bucket classification, and detailed flagging explanations.
- **Glassmorphism UI:** A premium, interactive interface designed for high-end stakeholder presentations.

## 📂 Project Structure
- `src/ai/app.py`: FastAPI backend, SSE streaming for research flow, and logging endpoints.
- `src/ai/search.py`: Core logic for Vector Search, Recursive Audits, and Gemini 3 Synthesis.
- `src/ai/static/index.html`: Fully reactive Glassmorphism frontend with Protocol Trace and Trends components.
- `scripts/research_logs_schema.sql`: Schema for user query and AI response tracking.
- `scripts/phase2_schema_update.sql`: Base database migration for vector-search and metadata support.

---

## 🛠️ Diagnostics
If you encounter issues, visit:
`http://localhost:8000/api/debug-db`
This will check if your Supabase function signature matches the expected frontend metadata.
