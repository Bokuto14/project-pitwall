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

### 🔮 Stage 3: The "What-If" Logic
**Goal:** Stitch real data with simulated data.
*   **Task A:** Build `simulate_strategy(driver, pit_lap, new_compound)`.
*   **Task B:** Merge "Virtual Driver" back into main dataset.

### 📊 Stage 4: The UI & Deploy
**Goal:** interactive dashboard.
*   **Task A:** Build Streamlit Sidebar (Select Race, Driver, Slider for Pit Lap).
*   **Task B:** Plot "Gap to Leader" graph using Plotly.

## 📜 Ground Rules

1.  **Clean Data**: Data must be well-labelled and spaced for easy understanding and future editing. Do not complicate the data structure.
2.  **Ask First**: If unable to access resources or if a decision between two paths is needed, ask the user for clarification.
3.  **Confirm Steps**: Do not proceed to the next stage without explicit confirmation from the user.
