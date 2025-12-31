import os
from dotenv import load_dotenv
from supabase import create_client

def check_legacy_trends():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Checking for legacy 'Google Trends' records in 'social_posts'...")
        # Check platform distribution first to see if they still exist
        p_resp = supabase.table("social_posts").select("platform", count="exact").ilike("platform", "%Google Trends%").execute()
        print(f"Legacy Google Trends records remaining: {p_resp.count}")
        
        if p_resp.count > 0:
            # Fetch a few to see the structure/keywords
            data_resp = supabase.table("social_posts").select("*").ilike("platform", "%Google Trends%").limit(20).execute()
            for i, row in enumerate(data_resp.data):
                print(f"\nRow {i+1}:")
                print(f"Content: {row.get('content')}")
                print(f"Bucket: {row.get('bucket_id')}")
                print(f"Platform: {row.get('platform')}")
        else:
            print("No legacy Google Trends records found in 'social_posts'. They might have been deleted after migration.")
            
            # If deleted, maybe there's a backup or we can look for the "real" keywords elsewhere.
            # Let's check common bucket_ids that might relate to trends.
            b_resp = supabase.table("social_posts").select("bucket_id").execute()
            buckets = sorted(list(set([r['bucket_id'] for r in b_resp.data if r['bucket_id']])))
            print("\nDistinct buckets in social_posts:", buckets)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_legacy_trends()
