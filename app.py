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

# Map
fig3 = px.scatter_mapbox(df_filtered, lat='Latitude', lon='Longitude',
                         color='Plastic_Type', size='Plastic_Weight_kg',
                         title='Plastic Pollution by Type and Location',
                         mapbox_style='open-street-map', zoom=1,
                         height=600)
st.plotly_chart(fig3)
