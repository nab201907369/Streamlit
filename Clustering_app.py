# %% 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.spatial.distance import cdist

# Setup Streamlit page
st.set_page_config(page_title='Lebanon Order Assignment', layout='wide')
st.title("📍 Lebanon Order Assignment Dashboard")

# Load full clustered dataset
@st.cache_data
def load_data():
    df = pd.read_csv("Final_dataset_with_clusters.csv")
    return df

df = load_data()

# Sidebar - Zone Selection
zones = sorted(df['recipient_zone_original'].unique())
selected_zone = st.sidebar.selectbox("📍 Select Zone", zones, index=zones.index('Beirut'))

# Filter data to selected zone
zone_df = df[df['recipient_zone_original'] == selected_zone].copy()

# Sample for speed if too many points
zone_df = zone_df.sample(min(len(zone_df), 1000), random_state=42)

# Compute cluster centers for the selected zone
cluster_centers = zone_df.groupby('cluster')[['latitude', 'longitude']].mean()

# Sidebar - New Order Input
st.sidebar.header("➕ Simulate New Order")
new_lat = st.sidebar.number_input("Latitude", value=zone_df['latitude'].mean(), format="%.6f")
new_lon = st.sidebar.number_input("Longitude", value=zone_df['longitude'].mean(), format="%.6f")
new_area = st.sidebar.text_input("Area Name", value=f"New Area, {selected_zone}")

if st.sidebar.button("🚀 Assign Order to Cluster"):
    # Distance calculation to zone's clusters
    distances = cdist([[new_lat, new_lon]], cluster_centers.values)
    nearest_cluster = cluster_centers.index[np.argmin(distances)]

    st.success(f"📦 Assigned to Cluster {nearest_cluster} in {selected_zone}")

    # Plot map for selected zone
    fig = px.scatter_mapbox(
        zone_df,
        lat='latitude',
        lon='longitude',
        color='cluster',
        hover_data=['recipient_area_original'],
        mapbox_style='open-street-map',
        zoom=10,
        height=700,
        category_orders={"cluster": sorted(zone_df['cluster'].unique())},
        color_continuous_scale=px.colors.qualitative.Set1,
        title=f"📍 Clusters in {selected_zone} (Updated)"
    )
    fig.update_traces(marker=dict(size=7))

    # Add new order marker
    new_marker = go.Scattermapbox(
        lat=[new_lat],
        lon=[new_lon],
        mode='markers',
        marker=dict(
            size=20 ,
            color='black',
            opacity=1.0
        ),
        name='📦 New Order',
        hovertext=[f"New Order - Cluster {nearest_cluster}"]
    )
    fig.add_trace(new_marker)

    # Add annotation
    fig.add_annotation(
        text=f"📦 Cluster {nearest_cluster}",
        x=new_lon,
        y=new_lat,
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(color="black", size=14),
        bgcolor="white",
        opacity=0.9
    )

    # Center map on new order
    fig.update_layout(mapbox=dict(center=dict(lat=new_lat, lon=new_lon), zoom=14))
    st.plotly_chart(fig, use_container_width=True)

else:
    # Show default map without assignment
    fig = px.scatter_mapbox(
        zone_df,
        lat='latitude',
        lon='longitude',
        color='cluster',
        hover_data=['recipient_area_original'],
        mapbox_style='open-street-map',
        zoom=10,
        height=700,
        category_orders={"cluster": sorted(zone_df['cluster'].unique())},
        color_continuous_scale=px.colors.qualitative.Set1,
        title=f"📍 Clusters in {selected_zone}"
    )
    fig.update_traces(marker=dict(size=7))
    st.plotly_chart(fig, use_container_width=True)
