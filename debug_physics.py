from src.data_loader import load_race_data
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Setup
pd.set_option('display.max_rows', 100)

def debug_soft_tires():
    print("🔍 Debugging Soft Tire Degradation...")
    df = load_race_data(2024, 'Bahrain')
    
    # Filter for Soft tires only, excluding In/Out laps
    soft_laps = df[
        (df['Compound'] == 'SOFT') & 
        (df['PitInTime'].isna()) & 
        (df['PitOutTime'].isna()) &
        (df['LapTimeSeconds'].notna())
    ].copy()
    
    print(f"\n📊 Total Soft Laps found: {len(soft_laps)}")
    
    # 1. Naive Regression (Current Implementation)
    X = soft_laps[['TyreLife']].values.reshape(-1, 1)
    y = soft_laps['LapTimeSeconds'].values
    
    model = LinearRegression()
    model.fit(X, y)
    print(f"❌ Current Naive Slope (Deg): {model.coef_[0]:.4f} s/lap")
    
    # 2. Fuel Correction Analysis
    # Standard F1 Fuel Effect is approx 0.06s faster per lap of fuel burned
    FUEL_CORRECTION = 0.06 
    
    # We add time BACK to the lap time as if fuel wasn't burning off
    # AdjustedTime = ActualTime + (LapNumber * FuelBurnEffect)
    soft_laps['FuelAdjustedTime'] = soft_laps['LapTimeSeconds'] + (soft_laps['LapNumber'] * FUEL_CORRECTION)
    
    y_adjusted = soft_laps['FuelAdjustedTime'].values
    model_adj = LinearRegression()
    model_adj.fit(X, y_adjusted)
    
    print(f"✅ Fuel Adjusted Slope (Deg): {model_adj.coef_[0]:.4f} s/lap")
    
    print("\n--- Detailed Data (First 20 rows) ---")
    print(soft_laps[['Driver', 'LapNumber', 'TyreLife', 'LapTimeSeconds', 'FuelAdjustedTime']].head(20))

if __name__ == "__main__":
    debug_soft_tires()
