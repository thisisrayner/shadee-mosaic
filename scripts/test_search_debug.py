import sys
import os
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.ai.search import SemanticSearch

def test_search():
    print("Initializing SemanticSearch...")
    try:
        search_engine = SemanticSearch()
        query = "stress"
        print(f"Running test search for: '{query}'")
        results = search_engine.search(query, limit=1)
        
        if results:
            print(f"SUCCESS: Found {len(results)} results.")
            print(results)
        else:
            print("WARNING: Search returned no results (but no error raised).")
            
    except Exception as e:
        print(f"ERROR: Search failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
