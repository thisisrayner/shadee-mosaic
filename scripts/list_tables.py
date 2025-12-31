import os
from dotenv import load_dotenv
from supabase import create_client

def list_all_tables():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Attempting to list tables in 'public' schema...")
        # We can query the information_schema via an RPC or raw query if we have a custom function.
        # But usually, we can try to guess or use a common diagnostic RPC.
        # Since we don't have a list_tables RPC, we'll try to use a common one or just check the ones we suspect.
        
        suspects = [
            'google_trends', 'social_posts', 'keywords', 'config', 
            'metadata', 'ingestion_log', 'youtube_comments', 'youtube_data'
        ]
        
        for table in suspects:
            try:
                res = supabase.table(table).select("count", count="exact").limit(0).execute()
                print(f"Table '{table}': {res.count} rows")
            except Exception:
                pass # Table not found

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_tables()
