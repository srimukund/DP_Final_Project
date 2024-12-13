import streamlit as st
import pandas as pd
from skmob import TrajDataFrame
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import numpy as np
from folium import Icon
from geopy.distance import geodesic

# Differential privacy function using Laplace mechanism
def add_laplace_noise(data, epsilon, sensitivity=1.0):
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale, size=data.shape)
    return data + noise

# Privacy risk assessment function (improved with geopy)
def assess_privacy_risk(traj_df, original_df):
    unique_users = traj_df['user_id'].nunique()
    total_points = traj_df.shape[0]
    
    # Calculate average geodesic distance between original and noisy points
    traj_df['orig_lat'] = original_df['lat'].values
    traj_df['orig_lng'] = original_df['lng'].values
    traj_df['distance'] = traj_df.apply(lambda row: geodesic((row['lat'], row['lng']), (row['orig_lat'], row['orig_lng'])).meters, axis=1)
    average_distance = traj_df['distance'].mean()
    
    # Adjust reidentification risk based on average distance
    reidentification_risk = (unique_users / total_points) * (1 / (1 + average_distance))
    
    return reidentification_risk

# Load the cleaned dataset
DATA_PATH = "/Users/srimukund/Desktop/transportation/cleaned_trajectories.csv"
data = pd.read_csv(DATA_PATH)

# Ensure proper data types
data['utc_date'] = pd.to_datetime(data['utc_date'])

# Rename columns for compatibility with TrajDataFrame
data.rename(columns={
    'caid': 'user_id',
    'latitude': 'lat',
    'longitude': 'lng',
    'state_pois': 'state'
}, inplace=True)

# Sort data by user and timestamp
data = data.sort_values(by=['user_id', 'utc_date'])

# Select only the necessary columns for TrajDataFrame
required_columns = ['lat', 'lng', 'utc_date', 'user_id']
data_for_traj = data[required_columns]

# Convert to TrajDataFrame
traj = TrajDataFrame(data_for_traj, latitude='lat', longitude='lng', datetime='utc_date', user_id='user_id')

# Rename 'uid' to 'user_id' in TrajDataFrame for consistency
traj.rename(columns={'uid': 'user_id'}, inplace=True)

# Initialize session state for noisy trajectory and toggle state
if 'noisy_traj' not in st.session_state:
    st.session_state.noisy_traj = None
if 'show_original' not in st.session_state:
    st.session_state.show_original = True

# Streamlit app
st.title('Trajectory Data Dashboard')

# Filters
user_ids = st.multiselect('Select User IDs', options=traj['user_id'].unique(), default=[])
date_range = st.date_input('Select Date Range', value=[traj['datetime'].min().date(), traj['datetime'].max().date()])

# Convert date_range to datetime
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

# Add a checkbox to select all users
select_all_users = st.checkbox('Select All Users')
if select_all_users:
    user_ids = traj['user_id'].unique().tolist()

# Add a slider to control the privacy parameter epsilon
epsilon = st.slider('Epsilon (Privacy Parameter)', min_value=0.1, max_value=10.0, value=1.0)

# Buttons to apply noise and show original trajectory
apply_noise = st.button('Apply Noise')
show_original = st.button('Show Original Trajectory')

# Filter the dataframe based on user inputs
filtered_traj = traj[(traj['user_id'].isin(user_ids)) &
                     (traj['datetime'].between(start_date, end_date))]

# Apply differential privacy if the "Apply Noise" button is clicked and save state
if apply_noise:
    st.session_state.noisy_traj = filtered_traj.copy()
    st.session_state.noisy_traj[['lat', 'lng']] = add_laplace_noise(filtered_traj[['lat', 'lng']], epsilon)
    st.session_state.show_original = False

# Toggle to show original trajectory if the "Show Original Trajectory" button is clicked
if show_original:
    st.session_state.show_original = True

# Determine which trajectory to display
if st.session_state.show_original or st.session_state.noisy_traj is None:
    display_traj = filtered_traj
else:
    display_traj = st.session_state.noisy_traj

# Check if the filtered DataFrame is empty
if display_traj.empty:
    st.write("No data available for the selected filters. Please adjust the filters and try again.")
else:
    # Privacy Risk Assessment
    privacy_risk = assess_privacy_risk(display_traj, filtered_traj)
    st.write(f"Reidentification Risk: {privacy_risk:.4f}")

    # Folium map centered on the filtered trajectories
    m = folium.Map(location=[display_traj['lat'].mean(), display_traj['lng'].mean()], zoom_start=12)

    # Add trajectory data to the map with tooltips and custom icons
    for index, row in display_traj.iterrows():
        folium.Marker(
            location=[row['lat'], row['lng']],
            icon=Icon(icon='arrow-up', prefix='fa', color='blue'),
            tooltip=f'User ID: {row["user_id"]}, Date: {row["datetime"]}'
        ).add_to(m)
        user_traj = display_traj[display_traj['user_id'] == row['user_id']]
        locations = user_traj[['lat', 'lng']].values.tolist()
        folium.PolyLine(locations, color='blue', weight=2.5, opacity=1).add_to(m)

    # Add HeatMap for additional insights
    heat_data = [[row['lat'], row['lng']] for index, row in display_traj.iterrows()]
    HeatMap(heat_data).add_to(m)

    # Adjust map zoom to fit all points
    bounds = display_traj[['lat', 'lng']].values.tolist()
    m.fit_bounds(bounds)

    # Display map
    st_folium(m, width=700, height=500)

    # Display filtered data
    st.write(display_traj)
