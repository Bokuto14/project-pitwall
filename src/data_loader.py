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
    Returns a dictionary with laps, results, and session info.
    """
    print(f"Loading {year} {grand_prix} - Session: {session_type}...")
    
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()
    
    laps = session.laps
    results = session.results
    
    # 1. Clean Laps
    needed_columns = [
        'Driver', 'LapNumber', 'LapTime', 
        'Compound', 'TyreLife', 'Stint', 
        'PitInTime', 'PitOutTime'
    ]
    available_columns = [col for col in needed_columns if col in laps.columns]
    clean_laps = laps[available_columns].copy()
    clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()
    clean_laps = clean_laps.sort_values(by=['Driver', 'LapNumber']).reset_index(drop=True)
    clean_laps['RaceTime'] = clean_laps.groupby('Driver')['LapTimeSeconds'].cumsum()
    
    # 2. Driver Results (for positions/teams)
    # Filter only drivers that participated
    results = results[results['Status'] != 'DidNotParticipate']
    
    return {
        'laps': clean_laps,
        'results': results,
        'event': session.event,
        'session_info': {
            'Year': year,
            'EventName': session.event['EventName'],
            'SessionName': session.name
        }
    }

def get_season_schedule(year):
    """
    Fetches the event schedule for a given year.
    Returns a DataFrame with EventName and Location.
    """
    try:
        schedule = fastf1.get_event_schedule(year)
        # Filter out testing sessions if possible, or just return all
        # FastF1 schedule includes 'Testing' in EventName usually
        return schedule[schedule['EventFormat'] != 'testing'][['EventName', 'Location', 'OfficialEventName', 'RoundNumber']]
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return pd.DataFrame()
