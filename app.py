import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_race_data, get_season_schedule
from src.physics import PhysicsEngine
from src.strategy import StrategyEngine
from src.track_utils import get_track_telemetry, plot_track_map

# --- Configuration ---
st.set_page_config(page_title="Project Pitwall", layout="wide", page_icon="🏎️")
st.title("🏎️ Project Pitwall: AI Strategy Simulator")

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Strategy Simulator"])

if page == "Home":
    st.markdown("""
    ## Welcome to Project Pitwall 🏁
    
    **Project Pitwall** is an advanced F1 Strategy Simulator that mimics the tools used by race engineers on the pit wall. 
    Replay historical races, test "What-If" scenarios, and see if you can outsmart the real strategists.
    
    ---
    
    ### 🆕 The 2026 Regulations: A New Era
    
    #### 1. The "Nimble Car" Concept 🏎️
    The era of "boats on wheels" is ending. The 2026 cars are designed to be smaller and more agile to improve wheel-to-wheel racing.
    *   **Lighter**: The minimum weight is dropping by 30kg (to 768kg).
    *   **Smaller**: The wheelbase (length) is shortened by 200mm, and the width is narrowed by 100mm.
    *   **Narrower Tires**: Pirelli is providing slimmer tires to reduce aerodynamic drag, though they remain on 18-inch rims.

    #### 2. Power Unit: The 50/50 Split 🔋
    The engine is becoming a true hybrid. While we keep the 1.6-liter V6 Turbo, the way it produces power is changing drastically.
    *   **Equal Power**: Output will be split roughly 50% internal combustion and 50% electric.
    *   **Electric Surge**: The electric motor (MGU-K) power is tripling—jumping from 120kW to 350kW.
    *   **Simplified Tech**: The complex MGU-H (which recovered heat from exhaust) is being removed to lower costs and attract new manufacturers like Audi and Ford.

    #### 3. Goodbye DRS, Hello "Active Aero" ✈️
    The traditional DRS (opening the rear wing) is being replaced by a more advanced system that affects both the front and rear wings.
    *   **X-Mode (Straight-line)**: On straights, wings "flatten" to reduce drag and increase top speed. Every driver can use this on every lap.
    *   **Z-Mode (Cornering)**: In corners, wings shift to high-downforce to "stick" the car to the track.
    *   **Overtake Mode**: Since everyone has Active Aero, overtaking is aided by a Manual Override. If a driver is within one second of the car ahead, they get a burst of extra electrical energy to help them pass.

    #### 4. 100% Sustainable Fuels 🌱
    F1 is going "Net Zero." For the first time, cars will run on fully sustainable "drop-in" fuels.
    *   These fuels are created from non-food sources, municipal waste, or even carbon captured directly from the atmosphere.
    *   **The Goal**: No new fossil carbon will be burned, making the internal combustion engine environmentally relevant for the future.
    """)

elif page == "Strategy Simulator":
    # --- Sidebar ---
    st.sidebar.markdown("---")
    @st.cache_data
    def get_schedule(y):
        return get_season_schedule(y)

    @st.cache_data
    def get_data(y, g, s):
        return load_race_data(y, g, s)

    @st.cache_data
    def get_track(y, g, s):
        return get_track_telemetry(y, g, s)

    # Sidebar Selection
    st.sidebar.markdown("---")
    st.sidebar.header("Race Configuration")
    
    # 1. Select Year
    year = st.sidebar.selectbox("Year", [2024, 2025])
    
    # 2. Get Schedule for Year
    schedule = get_schedule(year)
    
    if schedule.empty:
        st.error(f"Could not load schedule for {year}.")
        st.stop()
        
    # 3. Select GP
    # Use 'EventName' for display, but filter to ensure we get a valid one
    event_names = schedule['EventName'].tolist()
    
    # Default to Bahrain if available, else first
    default_ix = 0
    if "Bahrain Grand Prix" in event_names:
        default_ix = event_names.index("Bahrain Grand Prix")
        
    gp = st.sidebar.selectbox("Grand Prix", event_names, index=default_ix)
    
    # 4. Select Session
    session = st.sidebar.selectbox("Session", ["R", "Q", "SQ", "Sprint"], index=0)

    # Load Data
    with st.spinner(f"Loading {year} {gp}..."):
        try:
            data_dict = get_data(year, gp, session)
            race_data = data_dict # It returns a dict now
        except Exception as e:
            st.error(f"Could not load data: {e}")
            st.stop()

    # Initialize Engines
    physics = PhysicsEngine(race_data)
    strategy = StrategyEngine(race_data, physics)

    # Driver Selection
    drivers = sorted(race_data['laps']['Driver'].unique())
    selected_driver = st.sidebar.selectbox("Select Driver", drivers, index=drivers.index('VER') if 'VER' in drivers else 0)

    # Reality Check Toggle
    st.sidebar.markdown("---")
    st.sidebar.subheader("Analytics Settings")
    show_reality = st.sidebar.checkbox("Compare with Actual Race", value=True, help="Overlay actual historical lap times for verification.")

    # Strategy Controls
    st.sidebar.subheader("Strategy Plan")
    start_compound = st.sidebar.selectbox("Start Compound", ['SOFT', 'MEDIUM', 'HARD'], index=0)
    end_compound = st.sidebar.selectbox("Switch To", ['SOFT', 'MEDIUM', 'HARD'], index=2)

    total_laps = int(race_data['laps']['LapNumber'].max())
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
        
        # 1. ACTUAL REALITY (Validation)
        if show_reality:
            real_driver_data = race_data['laps'][race_data['laps']['Driver'] == selected_driver]
            fig_trace.add_trace(go.Scatter(
                x=real_driver_data['LapNumber'], 
                y=real_driver_data['LapTimeSeconds'],
                mode='lines',
                name='Historical Reality',
                line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dot')
            ))
        
        # 2. SIMULATED PREDICTION
        fig_trace.add_trace(go.Scatter(
            x=sim_results['LapNumber'], 
            y=sim_results['LapTime'],
            mode='lines',
            name='Pitwall Prediction',
            line=dict(color='cyan', width=3)
        ))
        
        # Mark Pit Stop
        
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

    # --- TRACK MAP & DETAILS ---
    st.sidebar.markdown("---")
    show_track = st.sidebar.toggle("Show Track Layout", value=True)
    
    if show_track:
        st.divider()
        col_t1, col_t2 = st.columns([1, 2])
        
        with col_t1:
            st.subheader("📍 Track Layout")
            try:
                track_telemetry = get_track(year, gp, session)
                fig_track = plot_track_map(track_telemetry)
                st.plotly_chart(fig_track, use_container_width=True)
            except Exception as e:
                st.error(f"Telemetry Unavailable: {e}")
        
        with col_t2:
            st.subheader("ℹ️ Race Details")
            event = race_data['event']
            st.info(f"**{event['EventName']}** | {event['Location']}, {event['Country']}")
            
            # Show top 3 in actual race
            results = race_data['results'].head(3)
            cols = st.columns(3)
            for i, (_, row) in enumerate(results.iterrows()):
                cols[i].markdown(f"""
                **P{i+1}: {row['FullName']}**  
                _{row['TeamName']}_
                """)
