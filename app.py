
"""
Program Name: Phone Use Statistics & Analysis
Author: Noah Ricke
Class: Advanced Data Modeling, WLC, Spring 2026
Program Description: Runs statistics & analysis on phone use dataset
Date: May 2, 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. DATA LOADING & CACHING ---
# Caching is used to reflect the "additional enhancements" requested in the assignment.
@st.cache_data
def get_my_data():
    # Reads the "user_behavior dataset into the 'my_df' variable.
    my_df = pd.read_csv("user_behavior_dataset.csv")
    return my_df

#Phone_data read into memory to allow for easy "calls" later in the program.
phone_data = get_my_data()

# --- 2. CUSTOM STYLING (CSS) ---
# This section was entirely the idea of Google Gemini and not something I would've programmed
# This section adds a white background and borders to the KPI boxes to make them look professional.
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #eeeeee;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD HEADER & ANALYTICAL QUESTION ---
# The title for the Streatmlit page and analytical question are defined here.
st.title("⌛📱📊 Phone Use Statistics & Analysis")
st.markdown("### How does phone use compare across user gender and user age?")
st.write("---")

# --- 4. SIDEBAR FILTERS ---
# Sidebar filters are created for gender and age group of the user.
st.sidebar.header("Filter the Data")

# The user can select "All," "Male," or "Female"
genders = ["All"] + phone_data['Gender'].unique().tolist()
pick_gender = st.sidebar.selectbox("Select Gender:", options=genders)

# The user can select age groups, with the default status being all ages selected. 
age_buckets = {
    "18 - 24": (18, 24),
    "25 - 34": (25, 34),
    "35 - 44": (35, 44),
    "45 - 54": (46, 54),
    "55+": (55, 100)
}
pick_ages = st.sidebar.multiselect("Select Age Range(s):", options=list(age_buckets.keys()), default=list(age_buckets.keys()))

# A new dataframe is created based on user filters.
working_df = phone_data.copy()

if pick_gender != "All":
    working_df = working_df[working_df['Gender'] == pick_gender]
    
# This codebase is beyond my understanding. Google Gemini wrote the code to allow
# for the age group selection to be made. 

if pick_ages:
    mask = pd.Series(False, index=working_df.index)
    for group in pick_ages:
        low, high = age_buckets[group]
        mask = mask | ((working_df['Age'] >= low) & (working_df['Age'] <= high))
    working_df = working_df[mask]

# --- 5. KPI METRICS ---
# For the filtered dataset, the following variables represent average app usage, number of apps, and data usage.
current_usage = working_df['App Usage Time (min/day)'].mean()
current_apps = working_df['Number of Apps Installed'].mean()
current_data = working_df['Data Usage (MB/day)'].mean()

# For the unfiltered dataset, the following variables represent average app usage, number of apps, and data usage.
all_usage = phone_data['App Usage Time (min/day)'].mean()
all_apps = phone_data['Number of Apps Installed'].mean()
all_data = phone_data['Data Usage (MB/day)'].mean()

# The following variables calculate percent differences from the unfiltered dataset baseline
usage_diff = ((current_usage - all_usage) / all_usage) * 100
apps_diff = ((current_apps - all_apps) / all_apps) * 100
data_diff = ((current_data - all_data) / all_data) * 100

# st.columns allows the KPIs to be displayed side by side.
k_col1, k_col2, k_col3 = st.columns(3)

with k_col1:
    # Average app usage for the filtered dataset against the baseline
    st.metric(label="App Usage Time", value=f"{current_usage:.0f} Min", delta=f"{usage_diff:.1f}% vs Avg")

with k_col2:
    # Average number of apps installed for the filtered dataset against the baseline.
    st.metric(label="Apps Installed", value=f"{current_apps:.0f} Apps", delta=f"{apps_diff:.1f}% vs Avg")

with k_col3:
    # Average data usage for the filtered dataset against the baseline
    st.metric(label="Data Usage", value=f"{current_data:.0f} MB", delta=f"{data_diff:.1f}% vs Avg")

st.write("---")

# --- 6. VISUALIZATIONS ---

# Bar Chart: A bar chart of average minutes of usage for every age in our filtered data.
bar_stats = working_df.groupby("Age")["App Usage Time (min/day)"].mean().reset_index()
usage_bar = px.bar(bar_stats, x="Age", y="App Usage Time (min/day)", title="Average Daily Usage by Age")
st.plotly_chart(usage_bar, use_container_width=True) # The chart fills the container width for better layout.

# st.columsn allows for the visualizations to be displayed side by side.
chart_left, chart_right = st.columns(2)

with chart_left:
    # Box Plot: The visuals shows app usage across genders, in a box plot format
    gender_box = px.box(working_df, x="Gender", y="App Usage Time (min/day)", color="Gender", title="Usage Distribution by Gender")
    st.plotly_chart(gender_box, use_container_width=True) # The chart fills the container width for better layout.

with chart_right:
    # Scatter Plot: This visual plots number of apps installed with app usage, applying a trendline.
    app_scatter = px.scatter(working_df, x="Number of Apps Installed", y="App Usage Time (min/day)", color="Operating System", trendline="ols", title="Apps vs. Usage Time")
    st.plotly_chart(app_scatter, use_container_width=True) # The chart fills the container width for better layout.

# --- 7. KEY FINDINGS ---
st.header("💡 Key Findings")
st.markdown("""
* Phone use time between male and female users is under a 1% difference, suggesting gender does not a critical factor in phone use.
* Age groups 18 - 24 and 45 - 54 report the highest app usage minutes, indicating a stereotype youth glued to the phone may be false.
* A positive trendline exists between app install and screen time use, enforcing the more applications on a phone, the more time a user spends on a phone.
""")

# --- 8. DATA TABLE & EXPORT ---
# The user has the option to download the filtered data.
st.subheader("Raw Filtered Data")
st.dataframe(working_df)

# Export Logic: This creates a CSV file that the user can download to their computer.
csv_ready = working_df.to_csv() # index=False, encode='utf-8' 
st.download_button(label="Download Filtered Data (CSV)", data=csv_ready, file_name="my_capstone_data.csv", mime="text/csv")