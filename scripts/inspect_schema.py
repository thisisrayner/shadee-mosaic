import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

def inspect_schema():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Fetching one row from social_posts...")
        response = supabase.table("social_posts").select("*").limit(1).execute()
        if response.data:
            print("Columns found:", response.data[0].keys())
            print("Sample data:", response.data[0])
        else:
            print("Table appears empty.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_schema()
