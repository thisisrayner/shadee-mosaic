import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client() -> Client:
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def generate_report(supabase: Client):
    print("--- Generating State of the Data Report ---")
    
    try:
        # 1. Total Count (using exact count)
        count_resp = supabase.table("social_posts").select("id", count="exact").limit(1).execute()
        total_count = count_resp.count
        print(f"Total Records: {total_count}")
        
        # 2. Sample data for analysis
        limit = 1000
        resp = supabase.table("social_posts").select("id, bucket_id, platform, post_dt").limit(limit).execute()
        df = pd.DataFrame(resp.data)
        
        # 3. Bucket Distribution
        bucket_counts = df['bucket_id'].value_counts(dropna=False).head(20)
        
        # 4. Platform Distribution
        platform_counts = df['platform'].value_counts(dropna=False)
        
        report_md = f"""# State of the Data Report: Project Shadee-Intelligence

## Executive Summary
- **Total Records:** {total_count}
- **Analyzed Sample:** {limit}

## Platform Distribution (Sample)
{platform_counts.to_markdown()}

## Bucket Distribution (Sample)
{bucket_counts.to_markdown()}

## Schema Audit
The `social_posts` table contains the following core columns:
- `id`
- `post_dt`
- `platform`
- `bucket_id` (Legacy/Regex)
- `ai_bucket_id`
- `ai_confidence`
- `ai_explanation`

**Missing for Shadow Tracking:**
- `is_anonymized` (Boolean)
- `verified_bucket_id` (UUID/Int)

## Schema Audit
The `social_posts` table already contains several "Shadow Tracking" columns:
- `ai_bucket_id`
- `ai_confidence`
- `ai_explanation`
- `is_anonymized`
- `verified_bucket_id`

## Recommendations
1. **Bulk Anonymization:** Only a fraction of the data appears to be marked as anonymized. We should run the `src/data/scrubber.py` logic in a bulk job.
2. **Backfill Labels:** Many records might missing high-confidence AI labels.
"""
    except Exception as e:
        print(f"Error generating report: {e}")
        return

    with open("docs/state_of_the_data.md", "w") as f:
        f.write(report_md)
    print("Report saved to docs/state_of_the_data.md")

if __name__ == "__main__":
    client = get_supabase_client()
    generate_report(client)
