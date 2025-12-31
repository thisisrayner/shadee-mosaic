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

    def search(self, query: str, threshold=0.5, limit=5, region: str = None):
        print(f"\n--- Searching Internal Brain for: '{query}' (Region: {region or 'All'}) ---")
        
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
                    "match_count": limit,
                    "filter_region": region
                }
            ).execute()
            
            results = resp.data
            if not results:
                print("No relevant narratives found.")
                return

            return results

        except Exception as e:
            print(f"Search error: {e}")

    def get_total_count(self, ai_only: bool = False, region: str = None):
        """Fetch total count of narratives according to specific toggle logic."""
        try:
            # Use count='planned' for fast estimation on large social_posts table
            query = self.supabase.table('social_posts').select('id', count='planned').limit(1)
            
            # Logic Rule 1 & 3: If verified on, filter by ai_bucket_id
            if ai_only:
                query = query.not_.is_('ai_bucket_id', 'null')
            
            # Logic Rule 3 & 4: If singapore on, filter by region SG or Singapore
            if region == "Singapore":
                # Ensure we capture both variants
                query = query.or_('region.ilike.Singapore,region.ilike.SG')
            elif region:
                query = query.ilike('region', region)

            res = query.execute()
            # If planned count returns 0 or None, try exact but with a very small slice
            if not res.count:
                res_exact = query.select('id', count='exact').limit(0).execute()
                return res_exact.count or 0
                
            return res.count
            
        except Exception as e:
            print(f"Count error: {e}")
            return 0

    def map_query_to_trend(self, query: str):
        """Map a user query to one of the tracked Google Trends keywords."""
        keywords = ["anxiety", "depression", "mental health", "self care", "therapy"]
        prompt = f"""
        You are a youth mental health specialist assistant.
        Given the user query: "{query}"
        
        Which of the following tracking categories is most semantically relevant to the intent behind this query?
        Categories: {', '.join(keywords)}
        
        If the query is clearly related to one of these, return ONLY the category name.
        If it is ambiguous or not related, return ONLY "NONE".
        Do not provide explanations.
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp') 
            response = model.generate_content(prompt)
            mapped = response.text.strip().lower()
            if mapped in keywords:
                return mapped
        except Exception as e:
            print(f"Mapping error: {e}")
        return None

    def get_trends_data(self, region: str = None, days: int = 180):
        """Fetch 180-day trend data for the 5 core keywords."""
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            query = self.supabase.table("google_trends")\
                .select("keyword, score, date")\
                .gte("date", cutoff_date)
            
            if region == "Singapore":
                query = query.eq("region", "Singapore")
            elif region:
                query = query.eq("region", region)
            else:
                query = query.eq("region", "Global") # Default to Global for trends

            resp = query.order("date").execute()
            return resp.data
        except Exception as e:
            print(f"Trends fetch error: {e}")
            return []


    async def research_flow(self, query: str, region: str = None):
        """
        An asynchronous generator that performs the Dynamic N research process.
        Yields status updates and finally the synthesis.
        """
        import json
        
        # Phase 1: Initial Sampling (Small N for quick audit)
        yield {"phase": "sampling", "status": "Sampling initial top 25 narratives...", "n": 25}
        yield {"phase": "log", "message": "Threshold: 0.1, Limit: 25", "data": {"threshold": 0.1, "limit": 25}}
        batch1 = self.search(query, threshold=0.1, limit=25, region=region)
        yield {"phase": "log", "message": f"Initial batch retrieved: {len(batch1 or [])} docs", "data": {"n": len(batch1 or [])}}
        
        if not batch1:
            yield {"phase": "error", "content": "No relevant narratives found for research sampling."}
            return

        # Phase 2: Saturation Audit
        yield {"phase": "audit", "status": "Auditing thematic saturation & variance...", "n": len(batch1)}
        
        audit_prompt = f"""
        Act as a Lead Clinical Researcher. 
        User Query: "{query}"
        Data: {len(batch1)} narratives.
        
        Analyze if these narratives reach "Thematic Saturation" (wherepatterns are stable and predictable) 
        or if they show "High Variance" (themes are fragmented or conflicting, suggesting a larger sample is needed).
        
        Return ONLY a JSON object:
        {{"decision": "SATURATED" or "EXPAND", "reason": "Short reason", "confidence": 0-100}}
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = await model.generate_content_async(audit_prompt)
            text = response.text.strip()
            # Robust JSON extraction
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                audit_result = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            yield {"phase": "audit_result", "decision": audit_result.get('decision', 'SATURATED'), "reason": audit_result.get('reason', 'N/A')}
            
            # Additional heuristic: If confidence is very low, bias towards Expansion
            decision = audit_result.get('decision', 'SATURATED')
            if audit_result.get('confidence', 100) < 40:
                decision = "EXPAND"
                yield {"phase": "audit_result", "decision": "EXPAND", "reason": "Low audit confidence, expanding for safety."}

            final_batch = batch1
            if decision == "EXPAND":
                # Phase 3: Expansion 1 (Middle N)
                yield {"phase": "sampling", "status": "Expanding sample to N=120 for statistical depth...", "n": 120}
                yield {"phase": "log", "message": "Expansion Threshold: 0.04, Limit: 120", "data": {"threshold": 0.04, "limit": 120}}
                batch2 = self.search(query, threshold=0.04, limit=120, region=region)
                final_batch = batch2 or batch1
                yield {"phase": "log", "message": f"Secondary batch retrieved: {len(batch2 or [])} docs", "data": {"n": len(batch2 or [])}}

                # Phase 3.5: Secondary Audit
                yield {"phase": "audit", "status": "Auditing secondary sample for saturation...", "n": len(final_batch)}
                try:
                    model_2 = genai.GenerativeModel('gemini-2.0-flash-exp')
                    response_2 = await model_2.generate_content_async(audit_prompt.replace(str(len(batch1)), str(len(final_batch))))
                    text_2 = response_2.text.strip()
                    if "{" in text_2 and "}" in text_2:
                        audit_result_2 = json.loads(text_2[text_2.find("{"):text_2.rfind("}")+1])
                        decision_2 = audit_result_2.get('decision', 'SATURATED')
                        yield {"phase": "audit_result", "decision": decision_2, "reason": audit_result_2.get('reason', 'N/A')}
                        
                        if decision_2 == "EXPAND":
                            yield {"phase": "sampling", "status": "Final Expansion to N=500 for maximum thematic capture...", "n": 500}
                            yield {"phase": "log", "message": "Final Expansion Threshold: 0.02, Limit: 500", "data": {"threshold": 0.02, "limit": 500}}
                            batch3 = self.search(query, threshold=0.02, limit=500, region=region)
                            final_batch = batch3 or final_batch
                            yield {"phase": "log", "message": f"Final batch retrieved: {len(batch3 or [])} docs", "data": {"n": len(batch3 or [])}}
                    else:
                        yield {"phase": "audit_result", "decision": "SATURATED", "reason": "Secondary audit inconclusive, using N=120"}
                except Exception as e:
                    print(f"Secondary Audit Error: {e}")
                    yield {"phase": "audit_result", "decision": "SATURATED", "reason": "Secondary audit failed, proceeding with current sample."}
            
        except Exception as e:
            print(f"Audit Error: {e}")
            final_batch = batch1 # Fallback
            yield {"phase": "audit_result", "decision": "SATURATED", "reason": "Audit failed, proceeding with initial sample."}

        # Phase 4: Final Synthesis
        yield {"phase": "synthesis", "status": f"Synthesizing {len(final_batch)} narratives...", "n": len(final_batch)}
        
        context = ""
        for i, r in enumerate(final_batch):
            content = r.get('content_scrubbed') or r.get('content') or "No content"
            context += f"Narrative {i+1}: {content}\n\n"

        synthesis_prompt = f"""
        SYSTEM ROLE: Senior Youth Mental Health Researcher.
        USER QUERY: "{query}"
        DATA SOURCE: {len(final_batch)} youth narratives.

        [RAW NARRATIVES]
        {context}

        ---
        [RESEARCH INSTRUCTIONS]
        Synthesize the {len(final_batch)} narratives above into a high-level research report.
        
        CRITICAL RULES:
        1. DO NOT repeat, echo, or list the individual narratives.
        2. DO NOT start your response with "Narrative 1:" or similar.
        3. Use a formal, objective, yet empathetic tone.
        4. Focus on aggregating themes and finding patterns.

        STRUCTURE YOUR REPORT IN MARKDOWN:
        # Clinical Research Synthesis: {query}
        
        ## 1. Primary Thematic Clusters
        (Synthesize the dominant emotional and situational patterns observed across the N={len(final_batch)} sample)
        
        ## 2. Evidence of Variance & Diverse Perspectives
        (Identify unique outliers or conflicting themes that emerged from the large sample size)
        
        ## 3. High-Level Stakeholder Recommendations
        (Provide actionable insights based on the collective patterns in the data)
        
        ## 4. Sampling & Saturation Note
        (Comment on the validity of an N={len(final_batch)} sample for this specific query)

        Begin synthesis immediately.
        """
        
        try:
            # Using Gemini 3 Flash for the final deep synthesis
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = await model.generate_content_async(synthesis_prompt)
            yield {"phase": "complete", "content": response.text, "n": len(final_batch)}
        except Exception as e:
            # Fallback to 2.0 if 3.0 is not yet available in this environment
            print(f"Gemini 3 Synthesis Error, falling back to 2.0: {e}")
            try:
                model_fb = genai.GenerativeModel('gemini-2.0-flash-exp')
                response_fb = await model_fb.generate_content_async(synthesis_prompt)
                yield {"phase": "complete", "content": response_fb.text, "n": len(final_batch)}
            except Exception as e2:
                yield {"phase": "error", "content": f"Synthesis Error: {str(e2)}"}

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
