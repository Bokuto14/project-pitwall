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
        
        # 2. Calculate Tire Degradation
        tire_deg = physics.calculate_tire_degradation()
        
        print("\n--- 🏁 Physics Constants for Bahrain 2024 ---")
        print(f"⏱️  Average Pit Loss: {pit_loss:.2f} seconds")
        print("📉 Tire Degradation (sec/lap):")
        for comp, deg in tire_deg.items():
            print(f"   - {comp}: {deg}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
