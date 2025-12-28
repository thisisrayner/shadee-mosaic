import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

print("--- Aggregating Platform Counts (Social Posts) ---")
# Since we have 55k rows, we'll use a count on each platform ilike query
platforms = ['Reddit', 'Tumblr', 'YouTube', 'Telegram', 'Google Trends']
for p in platforms:
    try:
        r = s.table("social_posts").select("id", count="exact").ilike("platform", f"%{p}%").execute()
        print(f"{p}: {r.count}")
    except Exception as e:
        print(f"Error counting {p}: {e}")

print("\n--- Checking for Other YouTube Tables ---")
potential_tables = ['youtube_comments', 'youtube_data', 'yt_narratives', 'social_listening_youtube', 'raw_youtube']
for t in potential_tables:
    try:
        r = s.table(t).select("id", count="exact").limit(0).execute()
        print(f"Table '{t}': {r.count} rows")
    except Exception:
        # Table likely doesn't exist or no permission
        pass
