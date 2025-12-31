import os
import time
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from scrubber import PIIScrubber # Reusing our Phase 1 scrubber

class BulkAnonymizer:
    """
    [⚠️ GUARDIAN WARNING]: NON-DESTRUCTIVE SHADOW PATTERN.
    This class MUST ONLY write to 'content_scrubbed'.
    NEVER overwrite the original 'content' column. 
    The 'content' column is the absolute source of truth for raw narratives.
    """
    def __init__(self, batch_size=50):
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase = create_client(url, key)
        self.scrubber = PIIScrubber()
        self.batch_size = batch_size

    def run(self, limit=1000):
        print(f"--- Starting Bulk Anonymization (Limit: {limit}) ---")
        
        # 1. Fetch pending rows
        try:
            # Targeted filter: Rows processed by AI but not yet anonymized
            resp = self.supabase.table("social_posts")\
                .select("id, content")\
                .not_.is_("ai_bucket_id", "null")\
                .or_("is_anonymized.eq.false,is_anonymized.is.null")\
                .limit(limit)\
                .execute()
            
            rows = resp.data
            if not rows:
                print("No pending rows found for anonymization.")
                return

            print(f"Found {len(rows)} rows to process.")
            
            # 2. Process in batches
            for i in range(0, len(rows), self.batch_size):
                batch = rows[i:i + self.batch_size]
                self._process_batch(batch)
                
        except Exception as e:
            print(f"Fatal error in bulk job: {e}")

    def _process_batch(self, batch):
        updates = []
        for row in batch:
            original_text = row.get("content")
            
            if not original_text:
                # Still mark as anonymized since there's no PII to scrub in NULL/Empty
                updates.append({
                    "id": row["id"],
                    "content": original_text,
                    "is_anonymized": True
                })
                continue
            
            scrubbed_text = self.scrubber.scrub(original_text)
            
            updates.append({
                "id": row["id"],
                "content_scrubbed": scrubbed_text,
                "is_anonymized": True
            })
        
        if updates:
            print(f"Updating batch of {len(updates)} rows...")
            success_count = 0
            for update_data in updates:
                try:
                    row_id = update_data.pop("id")
                    self.supabase.table("social_posts").update(update_data).eq("id", row_id).execute()
                    success_count += 1
                except Exception as e:
                    print(f"Error updating row {row_id}: {e}")
            
            print(f"Successfully updated {success_count}/{len(updates)} rows in this batch.")

if __name__ == "__main__":
    # Targeted run for AI-processed rows
    job = BulkAnonymizer(batch_size=50)
    job.run(limit=1300)
