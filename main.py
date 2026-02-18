from src.data_loader import load_race_data
from src.physics import PhysicsEngine
import pandas as pd

# Setup for display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def main():
    print("🏎️ Project Pitwall: Stage 2 - Physics Engine Verification")
    
    # Test Case: Bahrain 2024
    try:
        race_data = load_race_data(2024, 'Bahrain')
        
        if race_data.empty:
            print("❌ No data loaded.")
            return

        # Initialize Physics Engine
        physics = PhysicsEngine(race_data)
        
        # 1. Calculate Pit Loss
        pit_loss = physics.calculate_pit_loss()
        
        # 2. Calculate Tire Degradation (Non-Linear)
        tire_deg = physics.calculate_tire_degradation()
        
        print("\n--- 🏁 Physics Constants for Bahrain 2024 ---")
        print(f"⏱️  Average Pit Loss: {pit_loss:.2f} seconds")
        print("📉 Tire Degradation Models:")
        for comp, model in tire_deg.items():
            if model['type'] == 'linear':
                print(f"   - {comp} (Linear): +{model['params']:.3f} s/lap")
            else:
                p = model['params']
                print(f"   - {comp} (Exponential): Base={p[0]:.2f} | Rate={p[2]:.4f} (Cliff Detected!)")

        # 3. Simulate Strategy (Stage 3 Verification)
        print("\n--- 🔮 Strategy Simulation Test ---")
        from src.strategy import StrategyEngine
        strategy = StrategyEngine(race_data, physics)
        
        # Test: Simulate VER starting on Softs, pitting Lap 15 (Standard Strategy)
        sim_results = strategy.simulate_strategy('VER', 15, 'SOFT', 'HARD')
        
        if not sim_results.empty:
            print(f"\n✅ Simulated {len(sim_results)} laps for VER.")
            print(sim_results.head())
            print("...")
            
            # Check for Traffic
            traffic_laps = sim_results[sim_results['TrafficPenalty'] > 0]
            if not traffic_laps.empty:
                print(f"\n⚠️ TRAFFIC DETECTED on {len(traffic_laps)} laps!")
                print(traffic_laps[['LapNumber', 'LapTime', 'TrafficPenalty']].head())
            else:
                print("\n🏎️ Clean Air Race (No Traffic Detected)")
                
        else:
            print("❌ Simulation failed.")

    except Exception as e:
        print(f"\n❌ Error: {e}")


    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
