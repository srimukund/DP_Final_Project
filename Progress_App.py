import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import numpy as np

# Differential Privacy Function
def add_laplace_noise(data, epsilon, columns):
    """Adds Laplace noise to specified columns in the data."""
    for column in columns:
        sensitivity = data[column].max() - data[column].min()
        scale = sensitivity / epsilon
        data[column] = data[column] + np.random.laplace(0, scale, size=len(data))
    return data

# Load the cleaned dataset
DATA_PATH = "/Users/srimukund/Desktop/transportation/cleaned_trajectories.csv"
data = pd.read_csv(DATA_PATH)

# Ensure proper data types for filtering
data['utc_date'] = pd.to_datetime(data['utc_date'])

# Sort data by user and timestamp
data = data.sort_values(by=['caid', 'utc_date'])

# Sidebar filters
st.sidebar.header("Query Filters")

# Privacy Parameters
epsilon = st.sidebar.slider("Epsilon (Privacy Budget)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

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
    # Apply Differential Privacy
    filtered_data = add_laplace_noise(filtered_data, epsilon, ['latitude', 'longitude'])

    # Display filtered data for debugging
    st.write("### Filtered Data Preview (with Noise)", filtered_data.head())

    # Initialize the map centered on the data
    center_lat = filtered_data['latitude'].mean()
    center_lon = filtered_data['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Group trajectories by user and plot on the map
    for caid, group in filtered_data.groupby("caid"):
        group = group.sort_values(by="utc_date")
        points = list(zip(group['latitude'], group['longitude']))

        # Add a line for the trajectory
        folium.PolyLine(points, color="blue", weight=2.5, opacity=0.8, tooltip=f"User {caid}").add_to(m)

        # Add markers for start and end points
        folium.Marker(points[0], icon=folium.Icon(color='green', icon='info-sign'), tooltip=f"Start: User {caid}").add_to(m)
        folium.Marker(points[-1], icon=folium.Icon(color='red', icon='info-sign'), tooltip=f"End: User {caid}").add_to(m)

    # Cluster markers (optional, for visualization clarity)
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['utc_date']}",
        ).add_to(marker_cluster)

    # Display the map in Streamlit
    folium_static(m)
