import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from scipy.signal import argrelextrema
import numpy as np

def analyze_trend_rhythm():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)
    
    # Fetch data for a high-volume keyword to get a clear signal
    print("Fetching 'anxiety' trend data for Singapore...")
    resp = supabase.table("google_trends")\
        .select("date, score")\
        .eq("keyword", "anxiety")\
        .eq("region", "Singapore")\
        .order("date")\
        .execute()
    
    if not resp.data:
        print("No data found for 'anxiety' in Singapore. Trying Global...")
        resp = supabase.table("google_trends")\
            .select("date, score")\
            .eq("keyword", "anxiety")\
            .eq("region", "Global")\
            .order("date")\
            .execute()

    if not resp.data:
        print("No data found.")
        return

    df = pd.DataFrame(resp.data)
    df['date'] = pd.to_datetime(df['date'])
    df['day_name'] = df['date'].dt.day_name()
    df['score'] = df['score'].astype(float)
    
    # sort just in case
    df = df.sort_values('date')

    # Find local minima (valleys)
    # We use a comparison of 3 points (previous, current, next) to find a local valley
    n = 3  # neighbor comparison
    df['min'] = df.iloc[argrelextrema(df.score.values, np.less_equal, order=n)[0]]['score']
    
    valleys = df[df['min'].notnull()]
    
    print(f"\nAnalyzing {len(df)} days of data...")
    print(f"Found {len(valleys)} local valleys (low points).")
    
    print("\n--- Valley Day Distribution ---")
    print(valleys['day_name'].value_counts())
    
    print("\n--- Recent Valleys ---")
    print(valleys[['date', 'day_name', 'score']].tail(10).to_string(index=False))

if __name__ == "__main__":
    analyze_trend_rhythm()
