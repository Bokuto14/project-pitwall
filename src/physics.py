import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class PhysicsEngine:
    def __init__(self, race_data):
        self.data = race_data

    def calculate_pit_loss(self):
        """
        Calculates the time lost during a pit stop (Pit Loss).
        Logic: (InLapTime + OutLapTime) - (2 * AverageRacingLapTime)
        """
        print("🧮 Calculating Dynamic Pit Loss...")
        
        # 1. Identify Pit Stops
        # We need laps where PitInTime is not NaT (In Lap) and next lap is Out Lap
        # Actually easier: Find laps with PitInTime (InLap) and the SUBSEQUENT lap (OutLap)
        
        pit_in_laps = self.data[self.data['PitInTime'].notna()].copy()
        pit_losses = []

        for idx, in_lap in pit_in_laps.iterrows():
            driver = in_lap['Driver']
            lap_num = in_lap['LapNumber']
            
            # Find the Out Lap (LapNumber + 1) for the same driver
            out_lap = self.data[
                (self.data['Driver'] == driver) & 
                (self.data['LapNumber'] == lap_num + 1)
            ]
            
            if out_lap.empty:
                continue
            
            in_lap_time = in_lap['LapTimeSeconds']
            out_lap_time = out_lap.iloc[0]['LapTimeSeconds']
            
            if pd.isna(in_lap_time) or pd.isna(out_lap_time):
                continue

            # Calculate Driver's Base Pace (median of normal laps)
            # Filter clean laps: No Pit info, proper racing status (TrackStatus=1 ideally, but simpler: strict outlier check)
            driver_laps = self.data[self.data['Driver'] == driver]
            clean_laps = driver_laps[
                driver_laps['PitInTime'].isna() & 
                driver_laps['PitOutTime'].isna() &
                (driver_laps['LapTimeSeconds'] < in_lap_time) # Simple filter: Normal laps are faster than In-Laps
            ]
            
            if clean_laps.empty:
                continue
                
            base_pace = clean_laps['LapTimeSeconds'].median()
            
            # Pit Loss Formula
            # Actual Time spent covering 2 laps distance = InLap + OutLap
            # Expected Time if racing = 2 * BasePace
            # Loss = Actual - Expected
            loss = (in_lap_time + out_lap_time) - (2 * base_pace)
            pit_losses.append(loss)

        if not pit_losses:
            print("⚠️ Could not calculate Pit Loss. Defaulting to 22.0s.")
            return 22.0
            
        # Return median to be robust against outliers (slow stops)
        avg_pit_loss = np.median(pit_losses)
        print(f"✅ Calculated Average Pit Loss: {avg_pit_loss:.2f} seconds (Sample size: {len(pit_losses)} stops)")
        return avg_pit_loss

    def calculate_tire_degradation(self):
        """
        Calculates the degradation factor (seconds lost per lap of age) for each compound.
        Uses Linear Regression: (LapTime + FuelCorr) ~ TyreLife
        
        Fuel Correction: 0.06s gained per lap (standard F1 approximation).
        """
        print("📉 Calculating Tire Degradation Models...")
        
        compounds = self.data['Compound'].unique()
        deg_models = {}
        
        FUEL_CORRECTION = 0.06 # Seconds gained per lap due to fuel burn
        
        # Default fallbacks if regression fails or returns negative wear (getting faster)
        # This ensures the strategy engine doesn't suggest infinite stints.
        defaults = {
            'SOFT': 0.10,
            'MEDIUM': 0.06,
            'HARD': 0.04,
            'INTERMEDIATE': 0.0,
            'WET': 0.0
        }
        
        for compound in compounds:
            if compound not in defaults: 
                continue

            # Filter data for this compound
            # Exclude In/Out laps as they are slow/partial
            subset = self.data[
                (self.data['Compound'] == compound) &
                (self.data['PitInTime'].isna()) &
                (self.data['PitOutTime'].isna()) &
                (self.data['LapTimeSeconds'].notna())
            ].copy()
            
            # Filter outliers (Safety Car laps etc.)
            if subset.empty:
                deg_models[compound] = defaults.get(compound, 0.05)
                continue
                
            min_time = subset['LapTimeSeconds'].min()
            subset = subset[subset['LapTimeSeconds'] < min_time * 1.07]
            
            if len(subset) < 10:
                print(f"  ⚠️ Not enough data for {compound}. Using default.")
                deg_models[compound] = defaults.get(compound, 0.05)
                continue

            # Linear Regression on Fuel Adjusted Laps
            # Adjusted = LapTime + (LapNumber * FuelBurn)
            # This reveals true tire wear by removing the advantage of getting lighter.
            y_adjusted = subset['LapTimeSeconds'] + (subset['LapNumber'] * FUEL_CORRECTION)
            
            X = subset[['TyreLife']].values.reshape(-1, 1)
            y = y_adjusted.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            deg_per_lap = model.coef_[0]
            
            # Sanity Check: If degradation is still negative (track evolution > wear), 
            # we must clamp it to a small positive value for the simulation to make sense.
            if deg_per_lap <= 0:
                print(f"  ⚠️ {compound} showed negative wear ({deg_per_lap:.3f}). Clamping to default.")
                deg_per_lap = defaults.get(compound, 0.05)
            
            deg_models[compound] = float(f"{deg_per_lap:.3f}")
            print(f"  👉 {compound}: +{deg_models[compound]} s/lap")
            
        return deg_models
