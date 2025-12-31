import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

def check_regions():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    try:
        print("Fetching unique regions from social_posts...")
        # Since Supabase JS/Python client doesn't have a direct 'DISTINCT' on select,
        # we can use an RPC or just fetch a large sample and set it, 
        # but better yet, use a select with count to see what's there if possible.
        # Alternatively, perform a grouped query if RPC is available, 
        # or just fetch values and process in Python.
        
        response = supabase.table("social_posts").select("region").execute()
        if response.data:
            regions = {r['region'] for r in response.data if r['region']}
            print(f"Unique regions found: {regions}")
            
            # Specifically check for SG patterns
            sg_patterns = [r for r in regions if r and ('sg' in r.lower() or 'singapore' in r.lower())]
            print(f"SG-like values found: {sg_patterns}")
        else:
            print("No data found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_regions()
