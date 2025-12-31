import os
from dotenv import load_dotenv
from supabase import create_client

def inspect_keywords():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Querying unique keywords from 'google_trends'...")
        # Get count per keyword to see distribution
        # Note: Supabase Python SDK doesn't support GROUP BY directly in the same way 
        # as raw SQL, usually we'd use an RPC or just fetch a range.
        # But we can try a distinct query if available or just fetch top 100 rows.
        
        response = supabase.table("google_trends").select("keyword").limit(100).execute()
        
        keywords = [r['keyword'] for r in response.data]
        unique_keywords = set(keywords)
        
        print(f"Total rows fetched: {len(keywords)}")
        print(f"Unique keywords in first 100 rows: {unique_keywords}")
        
        # Let's try to get some that are NOT looks like numbers
        all_res = supabase.table("google_trends").select("keyword").execute()
        all_keywords = [r['keyword'] for r in all_res.data]
        unique_all = sorted(list(set(all_keywords)))
        
        print(f"Total unique keywords in entire table: {len(unique_all)}")
        print("First 20 unique keywords:", unique_all[:20])
        print("Last 20 unique keywords:", unique_all[-20:])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_keywords()
