import requests
import json

BASE_URL = "http://localhost:8001"

def test_trends_api():
    print("\n--- Testing Trends API ---")
    # Global Trends
    resp = requests.get(f"{BASE_URL}/api/trends?sg_only=false")
    data = resp.json().get('data', [])
    print(f"Global Trends: {len(data)} rows returned")
    if data:
        print(f"Sample Global Trend: {data[0]}")

    # SG Trends
    resp = requests.get(f"{BASE_URL}/api/trends?sg_only=true")
    data = resp.json().get('data', [])
    print(f"SG Trends: {len(data)} rows returned")
    if data:
        print(f"Sample SG Trend: {data[0]}")

def test_search_suggestion():
    print("\n--- Testing Search Suggestion Logic ---")
    # Clinical query with high threshold to trigger suggestion
    query = {
        "query": "chronic hopelessness and darkness",
        "limit": 5,
        "sg_only": True,
        "threshold": 0.95 
    }
    resp = requests.post(f"{BASE_URL}/api/search", json=query)
    data = resp.json()
    print(f"Query: {query['query']}")
    print(f"Results Count: {len(data.get('results', []))}")
    print(f"Mapped Keyword: {data.get('trend_keyword')}")
    print(f"Suggestion: {data.get('suggestion')}")

    # Test mapping specifically
    print("\n--- Testing Clinical Mapping ---")
    query_2 = {
        "query": "I can't stop crying and feel hopeless",
        "limit": 1,
        "sg_only": False
    }
    resp_2 = requests.post(f"{BASE_URL}/api/search", json=query_2)
    data_2 = resp_2.json()
    print(f"Query: {query_2['query']}")
    print(f"Mapped Keyword: {data_2.get('trend_keyword')}")

if __name__ == "__main__":
    try:
        test_trends_api()
        test_search_suggestion()
    except Exception as e:
        print(f"Error: {e}")
