import requests
import json

def test_research_streaming():
    url = "http://localhost:8001/api/research"
    payload = {
        "query": "exam stress and anxiety",
        "sg_only": False
    }
    
    print(f"Testing Research Stream: {url}")
    try:
        with requests.post(url, json=payload, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data = json.loads(decoded_line[6:])
                        print(f"[{data.get('phase')}] {data.get('status') or data.get('decision') or 'Content received...'}")
                        if data.get('phase') == 'complete':
                            print(f"\nFinal Synthesis (first 100 chars):\n{data.get('content')[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_research_streaming()
