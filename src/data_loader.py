import fastf1
import pandas as pd
import os

# Create a cache directory for FastF1
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)

def load_race_data(year, grand_prix, session_type='R'):
    """
    Loads and cleans race data for a specific Grand Prix.

    Args:
        year (int): The racing season year (e.g., 2024).
        grand_prix (str): The name or location of the GP (e.g., 'Bahrain').
        session_type (str): 'R' for Race, 'Q' for Qualifying. Default is 'R'.

    Returns:
        pd.DataFrame: A clean DataFrame containing lap times and tyre data.
    """
    print(f"Loading {year} {grand_prix} - Session: {session_type}...")
    
    # Load the session
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()
    
    # Extract laps
    laps = session.laps
    
    # Rule 1: Clean and Labelled Data
    # 1. Select only necessary columns
    needed_columns = [
        'Driver', 'LapNumber', 'LapTime', 
        'Compound', 'TyreLife', 'Stint', 
        'PitInTime', 'PitOutTime'
    ]
    
    # Filter columns that actually exist in the data to avoid errors
    available_columns = [col for col in needed_columns if col in laps.columns]
    clean_laps = laps[available_columns].copy()
    
    # 2. Convert LapTime to seconds (float) for calculations
    # FastF1 returns Timedelta, we need float seconds
    clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()
    
    # 3. Handle NaNs
    # Drop rows where LapTime is missing (e.g., first lap unscaled, or retired cars)
    # We keep them if valuable for other things, but for "Pace Analysis", we strictly need times.
    # For now, let's keep rows but ensure LapTimeSeconds is NaN where appropriate.
    
    # 4. Sort for readability
    clean_laps = clean_laps.sort_values(by=['Driver', 'LapNumber']).reset_index(drop=True)
    
    # 5. Calculate Cumulative Race Time per Driver
    # This is crucial for Traffic Analysis (finding where everyone else is at a specific time)
    # We use transform(cumsum) to keep the dataframe structure
    clean_laps['RaceTime'] = clean_laps.groupby('Driver')['LapTimeSeconds'].cumsum()
    
    print(f"Data Loaded: {len(clean_laps)} laps found.")
    return clean_laps
