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
