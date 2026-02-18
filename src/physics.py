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
        Calculates the degradation model for each compound.
        Attempts to fit an Exponential function: Time = A * exp(B * Age)
        This simulates the "Tire Cliff" where performance drops off non-linearly.
        
        Returns:
            dict: {Compound: {'model_type': 'exp'/'linear', 'params': (...)}}
        """
        print("📉 Calculating Tire Degradation Models (Non-Linear)...")
        from scipy.optimize import curve_fit
        
        compounds = self.data['Compound'].unique()
        deg_models = {}
        
        FUEL_CORRECTION = 0.06
        
        # Exponential function to fit: y = a + b * exp(c * x)
        # a = base pace, b = scale, c = wear rate (cliff steepness)
        def exp_deg_func(x, a, b, c):
            return a + b * np.exp(c * x)

        defaults = {
            'SOFT': 0.10, 'MEDIUM': 0.06, 'HARD': 0.04,
            'INTERMEDIATE': 0.0, 'WET': 0.0
        }
        
        for compound in compounds:
            if compound not in defaults: continue

            # Filter data
            subset = self.data[
                (self.data['Compound'] == compound) &
                (self.data['PitInTime'].isna()) &
                (self.data['PitOutTime'].isna()) &
                (self.data['LapTimeSeconds'].notna())
            ].copy()
            
            # Filter outliers
            if subset.empty:
                deg_models[compound] = {'type': 'linear', 'params': defaults.get(compound)}
                continue
                
            min_time = subset['LapTimeSeconds'].min()
            subset = subset[subset['LapTimeSeconds'] < min_time * 1.07]
            
            if len(subset) < 10:
                print(f"  ⚠️ Not enough data for {compound}. Using default linear.")
                deg_models[compound] = {'type': 'linear', 'params': defaults.get(compound)}
                continue

            # Prepare Data (Fuel Adjusted)
            y_adjusted = subset['LapTimeSeconds'] + (subset['LapNumber'] * FUEL_CORRECTION)
            x_data = subset['TyreLife'].values
            y_data = y_adjusted.values

            # Try Exponential Fit
            try:
                # Initial guesses: a=min_time, b=0.1, c=0.05
                popt, _ = curve_fit(exp_deg_func, x_data, y_data, p0=[min_time, 0.1, 0.05], maxfev=1000)
                
                # Check if the curve makes sense (c > 0 implies degradation)
                if popt[2] > 0:
                    deg_models[compound] = {'type': 'exponential', 'params': popt}
                    print(f"  👉 {compound}: Exponential Fit (Cliff Detected) | Rate: {popt[2]:.4f}")
                else:
                    raise ValueError("Negative wear rate in exp fit")
                    
            except Exception as e:
                # Fallback to Linear if exponential fit fails (or is flat/negative)
                X = x_data.reshape(-1, 1)
                model = LinearRegression()
                model.fit(X, y_data)
                slope = max(defaults.get(compound, 0.05), model.coef_[0])
                
                deg_models[compound] = {'type': 'linear', 'params': slope}
                print(f"  👉 {compound}: Linear Fit (Fallback) | Slope: {slope:.4f}")
            
        return deg_models
