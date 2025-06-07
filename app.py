import streamlit as st
import pandas as pd
import plotly.express as px


# Load data
@st.cache_data
def load_data():
    return pd.read_csv("ocean_plastic_pollution_data_cleaned.csv")

df = load_data()

st.title("🌊 Ocean Pollution Tracker")

# Sidebar filters
regions = df['Region'].unique()
selected_region = st.sidebar.multiselect("Select Region(s)", options=regions, default=regions)

plastic_types = df['Plastic_Type'].unique()
selected_types = st.sidebar.multiselect("Select Plastic Type(s)", options=plastic_types, default=plastic_types)

df_filtered = df[(df['Region'].isin(selected_region)) & (df['Plastic_Type'].isin(selected_types))]

# Summarize plastic weight by region
region_summary = df_filtered.groupby('Region')['Plastic_Weight_kg'].sum().reset_index()

fig = px.bar(region_summary, x='Region', y='Plastic_Weight_kg',
             title='Total Plastic Weight by Region',
             labels={'Plastic_Weight_kg':'Plastic Weight (kg)'},
             height=400)
st.plotly_chart(fig)

# Time trend
df_filtered['YearMonth'] = pd.to_datetime(df_filtered['Date']).dt.to_period('M')
time_summary = df_filtered.groupby('YearMonth')['Plastic_Weight_kg'].sum().reset_index()
time_summary['YearMonth'] = time_summary['YearMonth'].dt.to_timestamp()

fig2 = px.line(time_summary, x='YearMonth', y='Plastic_Weight_kg',
               title='Plastic Weight Over Time',
               labels={'YearMonth': 'Date', 'Plastic_Weight_kg': 'Plastic Weight (kg)'},
               height=400)
st.plotly_chart(fig2)


st.subheader("Plastic Pollution Map")

import folium
from streamlit_folium import st_folium

# Define a color palette for plastic types (add more if needed)
color_map = {
    'plastic_bottle': 'blue',
    'fishing_net': 'green',
    'plastic_bag': 'red',
    'microplastic': 'purple',
    'other': 'orange'
}

# Get unique plastic types in filtered data
unique_types = df_filtered['Plastic_Type'].unique()

# Assign colors dynamically if types not in predefined map
import random
import matplotlib.colors as mcolors

available_colors = list(mcolors.CSS4_COLORS.keys())
random.shuffle(available_colors)

for pt in unique_types:
    if pt not in color_map:
        color_map[pt] = available_colors.pop()

# Pacific Ocean approximate center and zoom
pacific_center = [-100, -260]  # Latitude 0, Longitude -160 approx central Pacific
zoom_level = 3

# Create Folium map centered on Pacific Ocean
m = folium.Map(location=pacific_center, zoom_start=zoom_level)

# Add markers with color by plastic type
for _, row in df_filtered.iterrows():
    color = color_map.get(row['Plastic_Type'], 'gray')
    popup_text = (f"Region: {row['Region']}<br>"
                  f"Plastic Type: {row['Plastic_Type']}<br>"
                  f"Weight (kg): {row['Plastic_Weight_kg']:.2f}<br>"
                  f"Depth (m): {row['Depth_meters']}")
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3 + (row['Plastic_Weight_kg'] ** 0.2),  # smaller radius with slight scaling
        popup=folium.Popup(popup_text, max_width=300),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        weight=1,
    ).add_to(m)

# Display map in Streamlit
st_data = st_folium(m, width=700, height=500)
