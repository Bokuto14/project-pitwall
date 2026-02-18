import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_race_data
from src.physics import PhysicsEngine
from src.strategy import StrategyEngine

# --- Configuration ---
st.set_page_config(page_title="Project Pitwall", layout="wide")
st.title("🏎️ Project Pitwall: AI Strategy Simulator")

# --- Sidebar ---
st.sidebar.header("Race Configuration")
year = st.sidebar.selectbox("Year", [2024])
gp = st.sidebar.selectbox("Grand Prix", ["Bahrain"])
session = st.sidebar.selectbox("Session", ["R"])

@st.cache_data
def get_data(y, g, s):
    return load_race_data(y, g, s)

with st.spinner("Loading Race Data..."):
    race_data = get_data(year, gp, session)

# Initialize Engines
physics = PhysicsEngine(race_data)
strategy = StrategyEngine(race_data, physics)

# Driver Selection
drivers = sorted(race_data['Driver'].unique())
selected_driver = st.sidebar.selectbox("Select Driver", drivers, index=drivers.index('VER') if 'VER' in drivers else 0)

# Strategy Controls
st.sidebar.subheader("Strategy Plan")
start_compound = st.sidebar.selectbox("Start Compound", ['SOFT', 'MEDIUM', 'HARD'], index=0)
end_compound = st.sidebar.selectbox("Switch To", ['SOFT', 'MEDIUM', 'HARD'], index=2)

total_laps = int(race_data['LapNumber'].max())
pit_lap = st.sidebar.slider("Pit Lap", min_value=1, max_value=total_laps-1, value=15)

# --- Main Analysis ---

# 1. Run Main Simulation
st.subheader(f"📊 Strategy Analysis: {selected_driver}")

col1, col2 = st.columns([2, 1])

with col1:
    with st.spinner(f"Simulating Strategy (Pit Lap {pit_lap})..."):
        sim_results = strategy.simulate_strategy(selected_driver, pit_lap, start_compound, end_compound)
    
    # Plot Race Trace
    fig_trace = go.Figure()
    
    # Real Data (Ghost) - if available
    # We don't have "Real Future" data for a live race, but for historical we do.
    # For now, let's just plot the Simulated path.
    
    fig_trace.add_trace(go.Scatter(
        x=sim_results['LapNumber'], 
        y=sim_results['LapTime'],
        mode='lines',
        name='Predicted Pace',
        line=dict(color='cyan')
    ))
    
    # Mark Pit Stop
    pit_data = sim_results[sim_results['Type'] == 'PIT']
    if not pit_data.empty:
        fig_trace.add_trace(go.Scatter(
            x=pit_data['LapNumber'],
            y=pit_data['LapTime'],
            mode='markers',
            name='Pit Stop',
            marker=dict(color='yellow', size=10, symbol='star')
        ))

    # Mark Traffic
    traffic_data = sim_results[sim_results['TrafficPenalty'] > 0]
    if not traffic_data.empty:
        fig_trace.add_trace(go.Scatter(
            x=traffic_data['LapNumber'],
            y=traffic_data['LapTime'],
            mode='markers',
            name='Traffic Delay',
            marker=dict(color='red', size=8, symbol='x')
        ))

    fig_trace.update_layout(
        title="Predicted Lap Times (Sec)",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (s)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_trace, use_container_width=True)

with col2:
    st.markdown("### 🚦 Pit Window Analysis")
    st.markdown("Where should you rejoin to avoid traffic?")
    
    with st.spinner("Analyzing Pit Window..."):
        window_results = strategy.analyze_pit_window(selected_driver, pit_lap, window_size=5)
    
    # Plot Horizontal Bar Chart for "Traffic Light"
    # Y-axis: Pit Lap
    # X-axis: Penalty (or a fixed bar colored by status)
    
    fig_window = go.Figure()
    
    fig_window.add_trace(go.Bar(
        y=window_results['PitLap'],
        x=[1]*len(window_results), # Fixed width bars
        orientation='h',
        marker=dict(
            color=window_results['Color'],
            line=dict(width=0)
        ),
        text=window_results['Status'],
        textposition='inside',
        hovertext=window_results['TrafficPenalty'].apply(lambda x: f"Penalty: {x:.2f}s")
    ))
    
    # Highlight Selected Lap
    fig_window.add_shape(
        type="line",
        x0=0, x1=1,
        y0=pit_lap, y1=pit_lap,
        line=dict(color="white", width=3, dash="dot"),
    )

    fig_window.update_layout(
        title="Pit Window Safety (Green=Clean, Red=Traffic)",
        xaxis=dict(showticklabels=False, title=""),
        yaxis=dict(title="Lap Number", tickmode='linear'),
        template="plotly_dark",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_window, use_container_width=True)

# --- Statistics ---
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Predicted Race Time", f"{sim_results['LapTime'].sum()/60:.2f} min")
c2.metric("Traffic Penalty", f"{sim_results['TrafficPenalty'].sum():.2f} s")
c3.metric("Compound Switch", f"{start_compound} ➔ {end_compound}")
