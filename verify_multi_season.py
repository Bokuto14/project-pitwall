import pandas as pd
from src.data_loader import get_season_schedule, load_race_data

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\n--- 🏁 Verifying Season Schedule API ---")

# 1. 2024 Schedule
try:
    s24 = get_season_schedule(2024)
    if not s24.empty:
        print(f"✅ 2024 Season: {len(s24)} races found.")
        print(s24[['EventName', 'Location']].head(3))
    else:
        print("❌ 2024 Schedule Empty!")
except Exception as e:
    print(f"❌ Error fetching 2024: {e}")

# 2. 2025 Schedule
try:
    s25 = get_season_schedule(2025)
    if not s25.empty:
        print(f"✅ 2025 Season: {len(s25)} races found.")
        print(s25[['EventName', 'Location']].head(3))
    else:
        print("⚠️ 2025 Schedule Empty (Expected if FastF1 hasn't updated yet, but API should return something).")
except Exception as e:
    print(f"❌ Error fetching 2025: {e}")

# 3. Data Loading Regression (Bahrain 2024)
print("\n--- 🏁 Regression Test: load_race_data (Bahrain 2024) ---")
try:
    data_dict = load_race_data(2024, "Bahrain")
    if isinstance(data_dict, dict) and 'laps' in data_dict:
        print("✅ Structured Data Returned Successfully (Dict format).")
        print(f"   - Laps: {len(data_dict['laps'])}")
        print(f"   - Event: {data_dict['event']['EventName']}")
    else:
        print("❌ Data Format Incorrect!")
except Exception as e:
    print(f"❌ Error loading data: {e}")
