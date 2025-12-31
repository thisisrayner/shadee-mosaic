import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

def debug_trends_data():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        # 1. Check all regions
        r_resp = supabase.table("google_trends").select("region").execute()
        regions = set([r['region'] for r in r_resp.data])
        print(f"Regions found: {regions}")

        # 2. Check all dates
        d_resp = supabase.table("google_trends").select("date").execute()
        dates = sorted(set([r['date'] for r in d_resp.data]))
        print(f"Total entries: {len(d_resp.data)}")
        if dates:
            print(f"Date range: {dates[0]} to {dates[-1]}")
        else:
            print("No dates found.")

        # 3. Check keywords
        k_resp = supabase.table("google_trends").select("keyword").execute()
        keywords = set([r['keyword'] for r in k_resp.data])
        print(f"Keywords found: {keywords}")

        # 4. Check query logic
        days = 180
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"Cutoff date (180 days ago): {cutoff_date}")
        
        # Try a query without region
        res = supabase.table("google_trends").select("*").gte("date", cutoff_date).limit(5).execute()
        print(f"Results with gte date but NO region: {len(res.data)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_trends_data()
