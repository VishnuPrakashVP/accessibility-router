import streamlit as st
import pandas as pd
import folium
import altair as alt
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.express as px

# Load CSV data
df_compare = pd.read_csv("../outputs/accessibility_stop_comparison.csv")
travel_times = {
    "normal": pd.read_csv("../outputs/travel_times_normal.csv"),
    "wheelchair": pd.read_csv("../outputs/travel_times_wheelchair.csv"),
    "elderly": pd.read_csv("../outputs/travel_times_elderly.csv")
}

st.set_page_config(layout="wide")
st.title("🧭 Accessibility Profile Comparison Dashboard")

# Sidebar
profile = st.sidebar.selectbox("Select profile", ["normal", "wheelchair", "elderly"])

# Metrics
st.subheader(f"📌 Key Metrics for '{profile}' Profile")
tt = travel_times[profile]
st.metric("🕒 Origin to Destination Travel Time (min)", int(tt.iloc[0]['travel_time']))

accessible_column = f"{profile}_accessible"
if accessible_column in df_compare.columns:
    accessible_count = df_compare[df_compare[accessible_column] == True].shape[0]
else:
    accessible_count = 0
st.metric("✅ Accessible Stops", accessible_count)
st.metric("📊 % Coverage", f"{round(accessible_count / df_compare.shape[0] * 100, 2)}%")

# Pie Chart: Accessible vs Not Accessible
st.subheader("🧩 Accessible vs Non-Accessible Stops")
pie_data = pd.Series({
    "Accessible": accessible_count,
    "Not Accessible": df_compare.shape[0] - accessible_count
})
fig, ax = plt.subplots()
pie_data.plot.pie(autopct='%1.1f%%', ylabel='', ax=ax)
st.pyplot(fig)

# Bar Chart of Stop Categories
st.subheader("📊 Stop Accessibility Overview by Category")
st.bar_chart(df_compare["category"].value_counts())

# Comparison Chart
st.subheader("📈 Travel Time Comparison Across Profiles")
comparison_df = pd.DataFrame({
    "Profile": list(travel_times.keys()),
    "Travel Time (min)": [int(travel_times[p].iloc[0]['travel_time']) for p in travel_times]
})
st.altair_chart(
    alt.Chart(comparison_df).mark_bar().encode(
        x='Profile',
        y='Travel Time (min)',
        color='Profile'
    ),
    use_container_width=True
)

# Map Embed
st.subheader(f"🗺️ Accessible Paths Map ({profile})")
map_path = f"../outputs/map_{profile}.html"
with open(map_path, 'r') as f:
    html = f.read()
st.components.v1.html(html, height=500)

# Summary Table with Deltas
st.subheader("📋 Profile Summary Table")
summary_data = {
    "Profile": [],
    "Travel Time (min)": [],
    "Accessible Stops": [],
    "Coverage (%)": [],
    "Time Delta (min)": []
}

normal_time = int(travel_times["normal"].iloc[0]['travel_time'])

for p in travel_times:
    travel_time = int(travel_times[p].iloc[0]['travel_time'])
    accessible_col = f"{p}_accessible"
    accessible_count = df_compare[df_compare[accessible_col] == True].shape[0] if accessible_col in df_compare.columns else 0
    coverage = round(accessible_count / df_compare.shape[0] * 100, 2) if df_compare.shape[0] > 0 else 0
    summary_data["Profile"].append(p)
    summary_data["Travel Time (min)"].append(travel_time)
    summary_data["Accessible Stops"].append(accessible_count)
    summary_data["Coverage (%)"].append(coverage)
    summary_data["Time Delta (min)"].append(travel_time - normal_time)

st.dataframe(pd.DataFrame(summary_data))

# Radar Chart Comparison
st.subheader("📡 Accessibility Coverage Radar")
radar_df = pd.DataFrame(summary_data)
fig_radar = px.line_polar(
    radar_df,
    r=radar_df["Coverage (%)"],
    theta=radar_df["Profile"],
    line_close=True,
    title="Coverage by Profile"
)
st.plotly_chart(fig_radar)

# Profile Info Summary
profile_info = {
    "normal": "No mobility restrictions, full access.",
    "wheelchair": "Needs smooth, step-free, and accessible paths.",
    "elderly": "Prefers safe, short, and well-lit walking routes."
}
st.sidebar.markdown("### ℹ️ Profile Info")
st.sidebar.info(profile_info[profile])

# Automatic Insight
st.subheader("🧠 Automatic Insight")
if summary_data["Time Delta (min)"][1] > 2:
    st.warning("⚠️ Elderly profile shows significant delay compared to normal.")
if summary_data["Coverage (%)"][2] < 10:
    st.warning("⚠️ Wheelchair accessibility is critically low in this area.")

# Enhanced Visual Analytics
st.subheader("📊 Profile Coverage Comparison")

# Bar chart with matplotlib
fig2, ax2 = plt.subplots()
profiles = summary_data["Profile"]
coverage = summary_data["Coverage (%)"]
ax2.bar(profiles, coverage, color=["green", "blue", "orange"])
ax2.set_ylabel("Coverage (%)")
ax2.set_title("Accessibility Coverage by Profile")
st.pyplot(fig2)

# Travel Time Delta Chart
st.subheader("⏱️ Time Delay Compared to Normal Profile")

fig3, ax3 = plt.subplots()
deltas = summary_data["Time Delta (min)"]
ax3.bar(profiles, deltas, color=["grey", "red", "purple"])
ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax3.set_ylabel("Time Difference (min)")
ax3.set_title("Extra Time Taken Compared to Normal Profile")
st.pyplot(fig3)