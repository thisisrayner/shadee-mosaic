import os
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

class VectorIndexer:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY must be set for indexing.")
            
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        genai.configure(api_key=self.gemini_key)
        self.model = "models/text-embedding-004"

    def get_embedding(self, text: str):
        """
        Generates a 768-dimensional vector embedding for the given text.
        
        Uses Gemini's 'text-embedding-004' model configured for 'retrieval_document'.
        """
        if not text:
            return None
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def run_batch(self, limit=100):
        print(f"--- Starting Embedding Generation (Limit: {limit}) ---")
        
        # 1. Fetch rows that are anonymized but have no embedding
        try:
            resp = self.supabase.table("social_posts")\
                .select("id, content_scrubbed")\
                .eq("is_anonymized", True)\
                .is_("embedding", "null")\
                .limit(limit)\
                .execute()
            
            rows = resp.data
            if not rows:
                print("No pending rows found for indexing.")
                return

            print(f"Found {len(rows)} rows to index.")
            
            # 2. Process and update
            success_count = 0
            for row in rows:
                text = row.get("content_scrubbed")
                if not text:
                    # If content is empty/null, we still mark it as indexed with a dummy or skip
                    # For RAG, we skip empty content
                    continue
                
                embedding = self.get_embedding(text)
                if embedding:
                    try:
                        self.supabase.table("social_posts")\
                            .update({"embedding": embedding})\
                            .eq("id", row["id"])\
                            .execute()
                        success_count += 1
                        if success_count % 10 == 0:
                            print(f"Indexed {success_count} rows...")
                    except Exception as e:
                        print(f"Error updating embedding for {row['id']}: {e}")
            
            print(f"Indexing complete. Total successful: {success_count}/{len(rows)}")
            
        except Exception as e:
            print(f"Fatal error in indexer: {e}")

if __name__ == "__main__":
    indexer = VectorIndexer()
    # Full indexing run for the current anonymized subset
    indexer.run_batch(limit=1400)
