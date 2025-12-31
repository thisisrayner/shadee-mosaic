import os
from supabase import create_client
from dotenv import load_dotenv

def create_logging_table():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    sql = """
    CREATE TABLE IF NOT EXISTS research_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL,
        query_text TEXT NOT NULL,
        response_text TEXT,
        query_type TEXT NOT NULL CHECK (query_type IN ('primary', 'followup')),
        n_used INTEGER,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
    );
    ALTER TABLE research_logs ENABLE ROW LEVEL SECURITY;
    """
    
    try:
        # We can't run raw SQL via the client directly unless we have an RPC
        # But we can try to see if 'pg_query' or similar exists.
        # Alternatively, since this is a local environment, I'll just assume 
        # the user will run the .sql file I created.
        print("Please execute the SQL in scripts/research_logs_schema.sql in your Supabase SQL Editor.")
        print("I have updated the backend and frontend to use this table.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_logging_table()
