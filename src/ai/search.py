import os
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
from tabulate import tabulate

class SemanticSearch:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY must be set for search.")
            
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        genai.configure(api_key=self.gemini_key)
        self.model = "models/text-embedding-004"

    def get_query_embedding(self, query: str):
        """Generate embedding for the search query."""
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None

    def search(self, query: str, threshold=0.5, limit=5):
        print(f"\n--- Searching Internal Brain for: '{query}' ---")
        
        query_embedding = self.get_query_embedding(query)
        if not query_embedding:
            return

        try:
            # Call the Supabase RPC function we created
            resp = self.supabase.rpc(
                "match_social_posts",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()
            
            results = resp.data
            if not results:
                print("No relevant narratives found.")
                return

            return results

        except Exception as e:
            print(f"Search error: {e}")

if __name__ == "__main__":
    engine = SemanticSearch()
    
    # Example test queries to show value
    queries = [
        "What are youth saying about exam stress and academic pressure?",
        "Narratives related to social anxiety or feeling lonely.",
        "Positive coping mechanisms or finding help."
    ]
    
    for q in queries:
        engine.search(q, limit=3)
