import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from matplotlib import cm
from matplotlib.colors import to_hex
import itertools
import hashlib

# Function to assign very distinct colors first, then use broader colors
def assign_color(caid, num_distinct_colors=20):
    distinct_colors = [
        "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",  # Primary distinct colors
        "#800000", "#808000", "#008000", "#800080", "#008080", "#000080",  # Secondary distinct colors
        "#FF5733", "#33FF57", "#5733FF", "#33FFF5", "#F533FF", "#F5FF33",  # Additional vibrant colors
        "#FFFFFF", "#000000"
    ]
    
    if len(distinct_colors) > num_distinct_colors:
        # Use distinct colors as primary
        return distinct_colors[int(hashlib.md5(str(caid).encode()).hexdigest(), 16) % num_distinct_colors]
    else:
        # Use a larger colormap for broader assignments
        colormap = cm.get_cmap("tab20b", num_distinct_colors)
        return to_hex(colormap(int(hashlib.md5(str(caid).encode()).hexdigest(), 16) % num_distinct_colors))

# Load the cleaned dataset
DATA_PATH = "/Users/srimukund/Desktop/transportation/cleaned_trajectories.csv"
data = pd.read_csv(DATA_PATH)

# Ensure proper data types for filtering
data['utc_date'] = pd.to_datetime(data['utc_date'])

# Sort data by user and timestamp
data = data.sort_values(by=['caid', 'utc_date'])

# Streamlit App Layout
st.title("User Trajectory Analysis (Filtered Dataset)")

# Sidebar filters
st.sidebar.header("Query Filters")

# State Dropdown
state_filter = st.sidebar.multiselect(
    "Select States (leave empty for all):",
    options=sorted(data['state_pois'].dropna().unique()),
    default=None
)

# Dynamically filter users based on the state selection
if state_filter:
    state_filtered_data = data[data['state_pois'].isin(state_filter)]
    available_users = sorted(state_filtered_data['caid'].unique())
else:
    state_filtered_data = data
    available_users = sorted(data['caid'].unique())

# User Dropdown (with "Select All Users" option)
all_users = ["Select All Users"] + available_users
user_filter = st.sidebar.multiselect(
    "Select Users (CAID):",
    options=all_users,
    default=None
)

# Filter the data
filtered_data = state_filtered_data.copy()

# Filter by users
if "Select All Users" not in user_filter and user_filter:
    filtered_data = filtered_data[filtered_data['caid'].isin(user_filter)]

# Require user selection
if not user_filter:
    st.warning("Please select at least one user (CAID) or choose 'Select All Users'.")
elif filtered_data.empty:
    st.warning("No data available for the selected filters.")
else:
    # Display filtered data for debugging
    st.write("### Filtered Data Preview", filtered_data)

    # Extract home points
    home_data = filtered_data[filtered_data['home_flag'] == True]

    # Initialize Plotly Figure
    fig = go.Figure()

    # Add lines with very distinct colors for each user's trajectory
    for caid, group in filtered_data.groupby("caid"):
        # Ensure the group is sorted
        group = group.sort_values(by="utc_date")
        # Assign a distinct color
        color = assign_color(caid)
        # Add trajectory line
        fig.add_trace(go.Scattermapbox(
            mode="lines+markers",
            lon=group['longitude'],
            lat=group['latitude'],
            marker=dict(size=8, color=color, opacity=0.8),  # Marker color
            line=dict(width=3, color=color),  # Line color
            name=f"User {caid} Trajectory",
            hoverinfo="text",
            text=group['utc_date'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Show time on hover
        ))

        # Add arrowhead at the end of the trajectory
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[group['longitude'].iloc[-1]],
            lat=[group['latitude'].iloc[-1]],
            marker=dict(size=12, symbol="triangle-up", color=color, opacity=0.8),
            name=f"User {caid} End Point"
        ))

    # Add home points as red markers
    if not home_data.empty:
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=home_data['longitude'],
            lat=home_data['latitude'],
            marker=dict(size=15, color='red', symbol="star"),
            name="Home Points"
        ))

    # Update layout for the map
    fig.update_layout(
        mapbox={
            'style': "carto-positron",
            'zoom': 5,
            'center': {
                'lon': filtered_data['longitude'].mean(),
                'lat': filtered_data['latitude'].mean()
            }
        },
        margin={"r":0,"t":0,"l":0,"b":0},
        legend={"title": "Legend"}
    )

    # Show map
    st.plotly_chart(fig, use_container_width=True)