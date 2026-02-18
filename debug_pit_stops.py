from src.data_loader import load_race_data
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def analyze_pit_stops():
    print("🔍 Analyzing Pit Stop Data for Bahrain 2024...")
    
    # Load data
    df = load_race_data(2024, 'Bahrain')
    
    # Filter for laps where a pit stop occurred
    # FastF1 usually marks pit status, but here we can check PitInTime or PitOutTime
    # Note: PitInTime is usually populated on the "In Lap" (entering pits)
    #       PitOutTime is usually populated on the "Out Lap" (leaving pits)
    
    pit_laps = df[df['PitInTime'].notna() | df['PitOutTime'].notna()].copy()
    
    if pit_laps.empty:
        print("❌ No pit stop timestamps found in the data.")
        return

    print(f"\n✅ Found {len(pit_laps)} laps with Pit metadata.")
    
    # Let's look at a specific driver to see the sequence
    driver = pit_laps['Driver'].iloc[0]
    print(f"\n--- Example Pit Sequence for Driver {driver} ---")
    driver_laps = df[df['Driver'] == driver]
    
    # Show context around the pit stop
    # Find lap number of first pit
    first_pit_lap = pit_laps[pit_laps['Driver'] == driver]['LapNumber'].iloc[0]
    
    mask = (driver_laps['LapNumber'] >= first_pit_lap - 1) & (driver_laps['LapNumber'] <= first_pit_lap + 2)
    print(driver_laps.loc[mask, ['Driver', 'LapNumber', 'LapTimeSeconds', 'PitInTime', 'PitOutTime']])

    # Calculate approximate Pit Lane Time for valid rows
    # Note: PitInTime and PitOutTime might be on different rows (In Lap vs Out Lap)
    # FastF1 documentation says:
    # PitInTime: Time when car crossed pit entry timing line
    # PitOutTime: Time when car crossed pit exit timing line
    
    # We can calculate "Stationary Time" if we have duration, but usually we care about "Total Pit Loss"
    # Total Pit Loss = (InLapTime + OutLapTime) - (2 * AverageRacePace)
    
    print("\n--- Pit Loss Calculation Logic ---")
    print("We can determine pit loss dynamically comparing these laps to normal laps.")

if __name__ == "__main__":
    analyze_pit_stops()
