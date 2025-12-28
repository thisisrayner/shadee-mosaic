import os
from supabase import create_client, Client
from dotenv import load_dotenv

def patch_consistency():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    print("--- Executing Shadow Content Consistency Patch ---")
    
    # Fetch rows where content_scrubbed is NULL but is_anonymized is TRUE
    resp = supabase.table("social_posts")\
        .select("id, content")\
        .eq("is_anonymized", True)\
        .is_("content_scrubbed", "null")\
        .execute()
    
    rows = resp.data
    if not rows:
        print("No rows found needing consistency patch.")
        return

    print(f"Found {len(rows)} rows to patch.")
    
    updates = []
    for row in rows:
        updates.append({
            "id": row["id"],
            "content_scrubbed": row["content"]
        })
    
    # Run individual updates for safety
    success_count = 0
    for update_data in updates:
        try:
            row_id = update_data.pop("id")
            supabase.table("social_posts").update(update_data).eq("id", row_id).execute()
            success_count += 1
            if success_count % 100 == 0:
                print(f"Patched {success_count} rows...")
        except Exception as e:
            print(f"Error patching row {row_id}: {e}")
    
    print(f"Consistency patch complete. Total patched: {success_count}/{len(updates)}")

if __name__ == "__main__":
    patch_consistency()
