import fastf1
import numpy as np
import plotly.graph_objects as go

def get_track_telemetry(year, gp, session_type='R'):
    """
    Fetches telemetry for a fast lap to reconstruct the track layout.
    """
    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=True, laps=True, weather=False)
    
    # Get the fastest lap to use as a track reference
    fastest_lap = session.laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry()
    
    return telemetry[['X', 'Y', 'Z', 'Source']]

def plot_track_map(telemetry, driver_pos=None):
    """
    Plots the track map using X and Y coordinates.
    """
    fig = go.Figure()

    # Plot track
    fig.add_trace(go.Scatter(
        x=telemetry['X'],
        y=telemetry['Y'],
        mode='lines',
        line=dict(color='gray', width=4),
        name='Track Layout',
        hoverinfo='skip'
    ))

    # Plot driver if provided
    if driver_pos is not None:
        fig.add_trace(go.Scatter(
            x=[driver_pos['X']],
            y=[driver_pos['Y']],
            mode='markers+text',
            marker=dict(color='red', size=12, symbol='car'),
            name=driver_pos['Driver'],
            text=[driver_pos['Driver']],
            textposition="top center"
        ))

    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        showlegend=False
    )
    
    return fig
