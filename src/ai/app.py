import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

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
    sg_only: Optional[bool] = False

class SearchResult(BaseModel):
    id: str
    similarity: Optional[float] = 0.0
    platform: str
    content_scrubbed: Optional[str] = None
    content: Optional[str] = None
    post_dt: Optional[str] = None
    ai_bucket_id: Optional[str] = None
    ai_explanation: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    suggestion: Optional[str] = None
    trend_keyword: Optional[str] = None

class SummarizeRequest(BaseModel):
    results: List[SearchResult]
    query: str

class FollowUpRequest(BaseModel):
    query: str
    context: str
    results: List[SearchResult]
    session_id: str

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

class ResearchRequest(BaseModel):
    query: str
    sg_only: Optional[bool] = False
    session_id: Optional[str] = None

@app.post("/api/research")
async def conduct_research(req: ResearchRequest):
    """
    Conducts an iterative research session with real-time status updates via SSE.
    
    This endpoint initiates the Dynamic Research Flow, performing multi-stage 
    sampling and auditing, and logging the final results for analytical tracking.
    """
    async def event_generator():
        try:
            async for update in search_engine.research_flow(
                req.query, 
                region="Singapore" if req.sg_only else None,
                session_id=req.session_id
            ):
                # Format as SSE (data: <json>\n\n)
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'phase': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/follow-up")
async def follow_up(req: FollowUpRequest):
    """
    Answers a one-turn follow-up question based on the research synthesis context.
    
    The question and AI answer are logged to the database under the current session ID.
    """
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
        
        answer = response.text
        
        # Log follow-up
        if req.session_id:
            await search_engine.log_research_query(
                session_id=req.session_id,
                query=req.query,
                query_type="followup",
                response=answer,
                metadata={"has_context": True}
            )
            
        return {"answer": answer}
    except Exception as e:
        print(f"Follow-up Error: {e}")
        return {"answer": "Error answering follow-up. Please try again."}

@app.get("/api/stats")
async def get_stats(ai_only: bool = False, sg_only: bool = False):
    """Get statistics of the internal brain with filters."""
    try:
        region = "Singapore" if sg_only else None
        count = search_engine.get_total_count(ai_only=ai_only, region=region)
        return {"total_posts": count}
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"total_posts": 0}

@app.post("/api/search", response_model=SearchResponse)
async def perform_search(search_query: SearchQuery):
    """Main search endpoint with trend mapping and suggestions."""
    try:
        region = "Singapore" if search_query.sg_only else None
        
        # 1. Fetch narratives
        results = search_engine.search(
            query=search_query.query,
            threshold=search_query.threshold,
            limit=search_query.limit * 2 if search_query.ai_only else search_query.limit,
            region=region
        )
        
        # Apply AI-only filter if requested
        if search_query.ai_only and results:
            results = [r for r in results if isinstance(r, dict) and r.get('ai_explanation')]
            results = results[:search_query.limit]
        elif results:
            results = results[:search_query.limit]

        # 2. Add Trend Context / Suggestions
        suggestion = None
        trend_keyword = None
        if results is None or len(results) < 5:
            trend_keyword = search_engine.map_query_to_trend(search_query.query)
            if trend_keyword:
                loc = "Singapore" if search_query.sg_only else "the world"
                suggestion = f"Narrative evidence for '{search_query.query}' is sparse, but Google searches for '{trend_keyword}' in {loc} are showing activity. Explore broader trends?"

        return {
            "results": results or [],
            "suggestion": suggestion,
            "trend_keyword": trend_keyword
        }
    except Exception as e:
        print(f"CRITICAL API ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends(sg_only: bool = False):
    """Get summarized trend data for the dashboard chart."""
    try:
        region = "Singapore" if sg_only else "Global"
        data = search_engine.get_trends_data(region=region)
        # Fallback to Global if SG is empty to show something useful
        if not data and sg_only:
            data = search_engine.get_trends_data(region="Global")
        return {"data": data}
    except Exception as e:
        print(f"Trends API Error: {e}")
        return {"data": []}

# Serve Static Files
app.mount("/", StaticFiles(directory="src/ai/static", html=True), name="static")

@app.get("/")
async def read_index():
    return FileResponse("src/ai/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
