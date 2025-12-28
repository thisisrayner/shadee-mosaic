import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client() -> Client:
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    return create_client(url, key)

def explore_schema(supabase: Client):
    print("--- Exploring Database Schema ---")
    tables_to_try = ["posts", "social_posts", "records", "narratives"]
    for table in tables_to_try:
        try:
            print(f"Trying table: {table}...")
            response = supabase.table(table).select("*").limit(1).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                print(f"Table '{table}' found. Columns: {list(df.columns)}")
                return table, list(df.columns)
            else:
                print(f"Table '{table}' is empty or not found.")
        except Exception as e:
            print(f"Error accessing '{table}': {e}")
    return None, None

def sample_data(supabase: Client, table: str, limit: int = 10):
    print(f"--- Sampling {limit} rows from '{table}' ---")
    try:
        # Check platform distribution
        count_resp = supabase.table(table).select("platform").execute()
        if count_resp.data:
            df_counts = pd.DataFrame(count_resp.data)
            print("\n--- Platform Distribution ---")
            print(df_counts['platform'].value_counts())
            
            # Specifically check for YouTube
            yt_count = len(df_counts[df_counts['platform'].str.contains('YouTube', case=False, na=False)])
            print(f"YouTube records found: {yt_count}")

        response = supabase.table(table).select("*").limit(limit).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            print(df.head())
            output_path = "docs/data_sample.csv"
            df.to_csv(output_path, index=False)
            print(f"Sample saved to {output_path}")
            return df
        else:
            print(f"No data found in '{table}'.")
            return None
    except Exception as e:
        print(f"Error sampling data: {e}")
        return None

if __name__ == "__main__":
    try:
        client = get_supabase_client()
        table_name, cols = explore_schema(client)
        if table_name and cols:
            sample_data(client, table_name)
    except Exception as e:
        print(f"Execution failed: {e}")
