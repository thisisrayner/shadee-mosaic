import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

print("--- YouTube Audit in social_posts ---")
r = s.table("social_posts").select("id, ai_bucket_id, is_anonymized").ilike("platform", "YouTube").execute()
yt_rows = r.data
print(f"Total YouTube rows: {len(yt_rows)}")

processed = [row for row in yt_rows if row.get("ai_bucket_id") is not None]
anonymized = [row for row in yt_rows if row.get("is_anonymized") is True]

print(f"AI Processed: {len(processed)}")
print(f"Anonymized: {len(anonymized)}")

print("\n--- Checking for other tables ---")
tables_to_check = ['youtube_comments', 'youtube_data', 'weekly_youtube_stats', 'social_listening_youtube']
for t in tables_to_check:
    try:
        r = s.table(t).select("count", count="exact").limit(0).execute()
        print(f"Table '{t}': {r.count} rows")
    except Exception:
        print(f"Table '{t}': Not found or no permission")
