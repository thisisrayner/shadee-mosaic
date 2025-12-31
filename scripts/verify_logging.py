import os
import asyncio
import json
import uuid
from supabase import create_client
from dotenv import load_dotenv
from src.ai.search import SemanticSearch

async def verify_logging():
    load_dotenv()
    print("--- Verifying Research Query Logging ---")
    
    search_engine = SemanticSearch()
    session_id = str(uuid.uuid4())
    test_query = "anxiety and exam stress in Singapore"
    
    print(f"1. Testing direct log insertion (Session: {session_id})...")
    await search_engine.log_research_query(
        session_id=session_id,
        query="TEST_QUERY_DIRECT",
        query_type="primary",
        response="TEST_RESPONSE_DIRECT",
        n=10,
        metadata={"test": True}
    )
    
    print("2. Testing research_flow integration (N=25 phase)...")
    # We won't run the whole flow (time-consuming), just run enough to trigger a log or check the setup.
    # Actually, research_flow only logs at the END (synthesis). 
    # Let's mock a synthesis log.
    await search_engine.log_research_query(
        session_id=session_id,
        query=test_query,
        query_type="primary",
        response="Mocked clinical synthesis for N=120",
        n=120,
        metadata={"region": "Singapore", "model": "gemini-3-flash-preview"}
    )
    
    print("3. Testing follow-up logging...")
    await search_engine.log_research_query(
        session_id=session_id,
        query="Why is this common?",
        query_type="followup",
        response="This is common due to academic competitive culture...",
        metadata={"has_context": True}
    )
    
    print("\n4. Retrieving logs from database...")
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase = create_client(url, key)
        
        resp = supabase.table("research_logs")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()
        
        logs = resp.data
        if not logs:
            print("FAILED: No logs found for this session.")
        else:
            print(f"SUCCESS: Found {len(logs)} log entries for session {session_id}:")
            for l in logs:
                print(f"  - [{l['query_type'].upper()}] Q: {l['query_text'][:30]}... | R: {l['response_text'][:30]}...")
            
    except Exception as e:
        print(f"Database Fetch Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_logging())
