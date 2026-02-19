import pandas as pd
import numpy as np

class StrategyEngine:
    def __init__(self, data_dict, physics_engine):
        if isinstance(data_dict, dict):
            self.data = data_dict['laps']
            self.full_data = data_dict
        else:
            self.data = data_dict
        self.physics = physics_engine
        
        # Pre-calculate constants
        self.pit_loss = self.physics.calculate_pit_loss()
        self.to_deg_models = self.physics.calculate_tire_degradation()

    def simulate_strategy(self, driver_code, pit_lap, start_compound, end_compound):
        """
        Simulates a 1-stop strategy.
        Uses REAL data for laps before the pit stop (to sync Race Time).
        Simulates laps from 'pit_lap' onwards.
        """
        print(f"🔮 Simulating Strategy for {driver_code}: Pit Lap {pit_lap} ({start_compound} -> {end_compound})")
        
        # 1. Get Driver Data and Base Pace
        driver_laps = self.data[self.data['Driver'] == driver_code].copy()
        if driver_laps.empty:
            print(f"❌ Driver {driver_code} not found.")
            return pd.DataFrame()

        # Base Pace (10th percentile of clean laps)
        clean_laps = driver_laps[
            driver_laps['PitInTime'].isna() & 
            driver_laps['PitOutTime'].isna() &
            (driver_laps['LapTimeSeconds'] < driver_laps['LapTimeSeconds'].min() * 1.05)
        ]
        base_pace = clean_laps['LapTimeSeconds'].quantile(0.1)
        print(f"   ℹ️ Base Pace Estimate: {base_pace:.3f}s")
        
        total_laps = int(self.data['LapNumber'].max())
        simulated_laps = []
        
        # 2. Hybrid Simulation Loop
        # Phase A: Reality (Laps 1 to pit_lap - 1)
        # We copy the actual race data because the strategy hasn't changed yet.
        
        pre_pit_laps = driver_laps[driver_laps['LapNumber'] < pit_lap].sort_values('LapNumber')
        current_race_time = 0.0
        
        if not pre_pit_laps.empty:
            current_race_time = pre_pit_laps['RaceTime'].iloc[-1]
            
            # Add these to our result
            for _, row in pre_pit_laps.iterrows():
                simulated_laps.append({
                    'LapNumber': int(row['LapNumber']),
                    'LapTime': row['LapTimeSeconds'],
                    'Compound': row['Compound'],
                    'TyreAge': row['TyreLife'],
                    'Type': 'REAL',
                    'TrafficPenalty': 0.0
                })
        
        # Phase B: Simulation (pit_lap onwards)
        current_compound = start_compound
        current_tyre_age = pre_pit_laps['TyreLife'].iloc[-1] if not pre_pit_laps.empty else 0
        
        # Optimization: distinct drivers for traffic check
        other_drivers = self.data['Driver'].unique()
        other_drivers = [d for d in other_drivers if d != driver_code]
        
        for lap in range(pit_lap, total_laps + 1):
            
            # --- PIT STOP LOGIC ---
            if lap == pit_lap:
                # IN LAP + PIT TIME
                deg_pen = self._get_deg_penalty(current_compound, current_tyre_age)
                lap_time = base_pace + deg_pen + self.pit_loss
                
                simulated_laps.append({
                    'LapNumber': lap,
                    'LapTime': lap_time,
                    'Compound': current_compound,
                    'TyreAge': current_tyre_age,
                    'Type': 'PIT',
                    'TrafficPenalty': 0.0
                })
                
                current_race_time += lap_time
                # Switch Tires
                current_compound = end_compound
                current_tyre_age = 0 
                continue
            
            # --- RACE LAP LOGIC ---
            current_tyre_age += 1
            deg_pen = self._get_deg_penalty(current_compound, current_tyre_age)
            fuel_benefit = (lap - 1) * 0.06
            
            # Undercut Logic: Warmup Penalty (Task 3.5 B)
            # Fresh tires are cold. Add penalty on the first flying lap (Age 1).
            warmup_penalty = 3.0 if current_tyre_age == 1 else 0.0
            
            clean_pace = base_pace + deg_pen - fuel_benefit + warmup_penalty
            
            # --- TRAFFIC CHECK (Stage 3.5 A) ---
            predicted_arrival_time = current_race_time + clean_pace
            traffic_penalty = 0.0
            
            # Find closest rival ahead
            rival_times = self.data[
                (self.data['LapNumber'] == lap) & 
                (self.data['Driver'].isin(other_drivers))
            ][['Driver', 'RaceTime']]
            
            min_gap = 999.0
            
            for _, rival in rival_times.iterrows():
                rival_time = rival['RaceTime']
                # Positive interval = I am behind.
                gap = predicted_arrival_time - rival_time
                
                if 0 < gap < 2.0: # 2.0s Threshold (Sensitive)
                    if gap < min_gap:
                        min_gap = gap
                        
                    rival_pace = self.data[
                        (self.data['LapNumber'] == lap) & 
                        (self.data['Driver'] == rival['Driver'])
                    ]['LapTimeSeconds'].values[0]
                    
                    if np.isnan(rival_pace): continue
                    
                    traffic_pace = rival_pace + 0.5 # Dirty Air
                    
                    if traffic_pace > clean_pace:
                        # Take the worst case (slowest car ahead)
                        penalty = traffic_pace - clean_pace
                        if penalty > traffic_penalty:
                            traffic_penalty = penalty
                            clean_pace = traffic_pace
            
            current_race_time += clean_pace
            
            simulated_laps.append({
                'LapNumber': lap,
                'LapTime': clean_pace,
                'Compound': current_compound,
                'TyreAge': current_tyre_age,
                'Type': 'RACE',
                'TrafficPenalty': traffic_penalty
            })
            
        return pd.DataFrame(simulated_laps)

    def _get_deg_penalty(self, compound, age):
        """Helper to safely calculate deg from models."""
        model = self.to_deg_models.get(compound, {'type': 'linear', 'params': 0.05})
        
        if model['type'] == 'linear':
            return model['params'] * age
        elif model['type'] == 'exponential':
            # y = a + b * exp(c * x) - a (we want the delta, not the absolute time from the curve)
            # Actually, the curve `exp_deg_func` returns the Total Lap Time (Fuel Adjusted).
            # We want the "Penalty vs Fresh Tire".
            # Penalty = Curve(Age) - Curve(0)
            p = model['params'] # [a, b, c]
            def func(x, a, b, c): return a + b * np.exp(c * x)
            
            base_perf = func(0, *p)
            current_perf = func(age, *p)
            return current_perf - base_perf
            
        return 0.0

    def analyze_pit_window(self, driver_code, center_lap, window_size=5):
        """
        Analyzes a range of pit laps (center +/- window) to rate them.
        Returns a list of dicts with Status (CLEAN/TRAFFIC) and Penalty.
        """
        results = []
        min_lap = max(2, center_lap - window_size)
        max_lap = min(int(self.data['LapNumber'].max()) - 2, center_lap + window_size)
        
        print(f"🚦 Analyzing Pit Window for {driver_code}: Laps {min_lap}-{max_lap}")
        
        for lap in range(min_lap, max_lap + 1):
            # Simulate basic Soft -> Hard strategy
            sim = self.simulate_strategy(driver_code, lap, 'SOFT', 'HARD')
            
            if sim.empty: continue
            
            # Analyze the first 3 laps AFTER the pit stop for traffic
            # Pit Lap is 'lap'. Out Lap is 'lap + 1'.
            # Check laps [lap+1, lap+3]
            post_pit_laps = sim[
                (sim['LapNumber'] > lap) & 
                (sim['LapNumber'] <= lap + 5)
            ]
            
            total_traffic_penalty = post_pit_laps['TrafficPenalty'].sum()
            
            status = 'CLEAN' if total_traffic_penalty < 0.5 else 'TRAFFIC'
            color = 'green' if status == 'CLEAN' else 'red'
            
            results.append({
                'PitLap': lap,
                'Status': status,
                'TrafficPenalty': total_traffic_penalty,
                'Color': color
            })
            
        return pd.DataFrame(results)
