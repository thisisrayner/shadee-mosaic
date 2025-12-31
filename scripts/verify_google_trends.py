import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

def verify_google_trends():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Checking for 'google_trends' table...")
        # Try to select one row to verify existence and schema
        response = supabase.table("google_trends").select("*").limit(1).execute()
        print("SUCCESS: 'google_trends' table exists.")
        if response.data:
            print("Columns found:", response.data[0].keys())
            print("Sample data:", response.data[0])
        else:
            print("Table found but it is currently empty.")
            
        # Also check count
        count_response = supabase.table("google_trends").select("*", count="exact").execute()
        print(f"Total rows in google_trends: {count_response.count}")

    except Exception as e:
        if "does not exist" in str(e).lower():
            print("ERROR: 'google_trends' table not found.")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    verify_google_trends()
