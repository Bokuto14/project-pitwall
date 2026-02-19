# 🏎️ Project Pitwall: F1 Strategy Simulator

**Project Pitwall** is an interactive Python application that allows Formula 1 fans to replay historical races and test "What-If" scenarios. By utilizing real telemetry data, users can modify pit stop laps and tire compounds to see if a different strategy would have changed the podium outcome.

## 🚀 Key Features
* **Race Replay:** Visualize the gap evolution of any past race using real lap times.
* **Strategy Overwrite:** Change a driver's pit lap (e.g., "Pit Norris on Lap 20 instead of 24").
* **Physics Engine:** Calculates tire degradation and fuel burn to predict lap times for the *new* strategy.
* **Outcome Prediction:** Generates a new "Virtual Race Graph" showing where the driver would have merged back into traffic.

## 🛠️ Tech Stack
* **Data Source:** `FastF1` (Official Timing & Telemetry data)
* **Backend:** `Python 3.10+`, `Pandas` (DataFrames), `NumPy` (Math)
* **Frontend:** `Streamlit` (Interactive Dashboard)
* **Visualization:** `Plotly` (Interactive Gap Charts)

## 🏗️ Architecture
[Data Layer]      [Logic Layer]             [Presentation Layer]
FastF1 API  --->  RaceSimulationEngine  --->  Streamlit UI
(Raw Laps)        (Tire Deg Models)           (Interactive Graphs)

## 📅 Project Roadmap

### 🏁 Stage 1: The Data Pipeline
**Goal:** Get clean data for a single race (e.g., Bahrain 2024) and display the actual lap times.
*   **Task A:** Fetch LapTimes excluding Safety Car laps using `FastF1`.
*   **Task B:** Clean data (convert string times to float, handle NaNs).

### 🛞 Stage 2: The Physics Engine
**Goal:** Create the math model that predicts how tires slow down over time.
*   **Task A:** Implement Linear Degradation Model ($LapTime_{pred} = BasePace + (DegPerLap \times LapAge) - (FuelBurn \times LapNumber)$).
*   **Task B:** Calculate "Pit Loss" constant.
*   **Task C:** **[NEW] The Tire "Cliff" (Non-Linear Math):** Replace linear models with Exponential/Sigmoid functions (`Base_Pace * (1 + (Wear_Factor ^ Lap_Count))`) to simulate catastrophic tire drop-off.

### 🔮 Stage 3: The "What-If" Logic
**Goal:** Stitch real data with simulated data.
*   **Task A:** Build `simulate_strategy(driver, pit_lap, new_compound)`.
*   **Task B:** Merge "Virtual Driver" back into main dataset.

### 🚀 Stage 3.5: The "Context" Layer (The Complexity Spike)
**Goal:** Make the simulation aware of other cars (Multi-Agent Simulation).
*   **Task A (Traffic Injection):** "Traffic Check" function. Only assume "Clean Air" pace if the gap to the car ahead is > 1.5s.
    *   **Logic:** If `Predicted_Pos` overlaps `Rival_Pos`:
    *   `Max_Speed = min(My_Pace, Rival_Pace)`
    *   `Penalty = +0.5s (Dirty Air)`
*   **Task B (The Undercut Logic):** accurate calculation of the "Out Lap" (cold tires).

### 📊 Stage 4: The UI & Deploy
**Goal:** interactive dashboard.
*   **Task A:** Build Streamlit Sidebar (Select Race, Driver, Slider for Pit Lap).
*   **Task B:** Plot "Gap to Leader" graph using Plotly.
*   **Task C:** **[NEW] Pit Window Visualization:** A "Traffic Light" bar chart showing gaps to cars behind.
    *   🟢 **Green Zone:** Clear air (Pit now!)
    *   🔴 **Red Zone:** Traffic / DRS Train (Do not pit!)

## 📜 Ground Rules

1.  **Clean Data**: Data must be well-labelled and spaced for easy understanding and future editing. Do not complicate the data structure.
2.  **Ask First**: If unable to access resources or if a decision between two paths is needed, ask the user for clarification.
3.  **Confirm Steps**: Do not proceed to the next stage without explicit confirmation from the user.



1. The "Nimble Car" Concept
The era of "boats on wheels" is ending. The 2026 cars are designed to be smaller and more agile to improve wheel-to-wheel racing.

Lighter: The minimum weight is dropping by 30kg (to 768kg).

Smaller: The wheelbase (length) is shortened by 200mm, and the width is narrowed by 100mm.

Narrower Tires: Pirelli is providing slimmer tires to reduce aerodynamic drag, though they remain on 18-inch rims.

🔋 2. Power Unit: The 50/50 Split
The engine is becoming a true hybrid. While we keep the 1.6-liter V6 Turbo, the way it produces power is changing drastically.

Equal Power: Output will be split roughly 50% internal combustion and 50% electric.

Electric Surge: The electric motor (MGU-K) power is tripling—jumping from 120kW to 350kW.

Simplified Tech: The complex MGU-H (which recovered heat from exhaust) is being removed to lower costs and attract new manufacturers like Audi and Ford.

✈️ 3. Goodbye DRS, Hello "Active Aero"
The traditional DRS (opening the rear wing) is being replaced by a more advanced system that affects both the front and rear wings.

X-Mode (Straight-line): On straights, wings "flatten" to reduce drag and increase top speed. Every driver can use this on every lap.

Z-Mode (Cornering): In corners, wings shift to high-downforce to "stick" the car to the track.

Overtake Mode: Since everyone has Active Aero, overtaking is aided by a Manual Override. If a driver is within one second of the car ahead, they get a burst of extra electrical energy to help them pass.
+1

🌱 4. 100% Sustainable Fuels
F1 is going "Net Zero." For the first time, cars will run on fully sustainable "drop-in" fuels.
+1

These fuels are created from non-food sources, municipal waste, or even carbon captured directly from the atmosphere.

The Goal: No new fossil carbon will be burned, making the internal combustion engine environmentally relevant for the future.