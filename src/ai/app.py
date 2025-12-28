import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

# Add project root to sys.path for robust imports
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.ai.search import SemanticSearch

app = FastAPI(title="Shadee-Intelligence: Internal Brain Explorer")

# Initialize Search Engine
search_engine = SemanticSearch()

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 12
    threshold: Optional[float] = 0.35
    ai_only: Optional[bool] = False

class SearchResult(BaseModel):
    id: str
    similarity: float
    platform: str
    content_scrubbed: Optional[str] = None
    content: Optional[str] = None
    post_dt: Optional[str] = None
    bucket_id: Optional[str] = None
    ai_bucket_id: Optional[str] = None
    ai_explanation: Optional[str] = None

class SummarizeRequest(BaseModel):
    results: List[SearchResult]
    query: str

class FollowUpRequest(BaseModel):
    query: str
    context: str
    results: List[SearchResult]

@app.get("/api/debug-db")
async def debug_db():
    """Diagnostic route to verify Supabase function signature."""
    try:
        # Try a dummy search to see what keys come back
        results = search_engine.search(query="test", limit=1)
        if not results:
            return {"status": "ok", "message": "Connection works, but no data found to test."}
        
        keys = list(results[0].keys())
        required = ["content", "ai_explanation", "ai_bucket_id"]
        missing = [k for k in required if k not in keys]
        
        return {
            "status": "warning" if missing else "ok",
            "columns_found": keys,
            "missing_columns": missing,
            "instruction": "If columns are missing, please re-run scripts/phase2_schema_update.sql in Supabase." if missing else "Schema is correct."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/summarize")
async def summarize_results(req: SummarizeRequest):
    """Generate a clinical synthesis of the search results."""
    try:
        if not req.results:
            return {"synthesis": "No narratives found to synthesize."}
        
        # Build context from results
        context = ""
        for i, r in enumerate(req.results):
            content = r.content_scrubbed or r.content or "No content"
            classification = "LLM Tier 2" if r.ai_explanation else "Regex Tier 1"
            context += f"Narrative {i+1} [{classification}]: {content}\n\n"

        prompt = f"""
        You are a trained therapy specialist in youth mental health for Project Shadee. 
        User Query: "{req.query}"
        
        Based on the provided {len(req.results)} narratives, please provide a high-level clinical synthesis.
        Identify:
        1. Core emotional themes or stressors.
        2. Common patterns in the youth narratives.
        3. Potential intervention focal points.
        
        Be concise, professional, and empathetic. Mention if the data contains baseline Regex classifications vs high-fidelity AI tier analysis.
        
        Narratives:
        {context}
        """
        
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return {"synthesis": response.text}
    except Exception as e:
        print(f"Summarization Error: {e}")
        return {"synthesis": "Error generating synthesis. Please try again later."}

@app.post("/api/follow-up")
async def follow_up(req: FollowUpRequest):
    """Answer a one-turn follow-up question based on the synthesis."""
    try:
        prompt = f"""
        You are a trained therapy specialist in youth mental health. You just provided a synthesis of narratives for the query "{req.query}".
        
        Original Synthesis:
        {req.context}
        
        User Follow-up Question: "{req.query}"
        
        Answer based on the provided narratives and the synthesis context.
        """
        
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return {"answer": response.text}
    except Exception as e:
        print(f"Follow-up Error: {e}")
        return {"answer": "Error answering follow-up. Please try again."}

@app.post("/api/search", response_model=List[SearchResult])
async def perform_search(search_query: SearchQuery):
    try:
        results = search_engine.search(
            query=search_query.query,
            threshold=search_query.threshold,
            limit=search_query.limit * 2 if search_query.ai_only else search_query.limit
        )
        if not results:
            return []
        
        # Apply AI-only filter if requested
        if search_query.ai_only:
            results = [r for r in results if r.get('ai_explanation')]
            results = results[:search_query.limit]
            
        return results
    except Exception as e:
        print(f"CRITICAL API ERROR: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal Search Error")

# Serve Static Files
app.mount("/", StaticFiles(directory="src/ai/static", html=True), name="static")

@app.get("/")
async def read_index():
    return FileResponse("src/ai/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
