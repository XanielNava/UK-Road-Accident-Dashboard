import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="UK Road Safety Dashboard", layout="wide")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Final_Dashboard_Data.csv", nrows=500000)
    return df

df = load_data()

# TITLE
st.title("UK Road Safety Intelligence Dashboard")
st.markdown("### By: Xaniel Nava, Yasmine Kate Bolivar, Aldrin Bansuelo")
st.markdown("---")

# SIDEBAR FILTERS
st.sidebar.header("Filters")

# Severity filter
severity_filter = st.sidebar.multiselect(
    "Accident Severity",
    options=df["accident_severity"].dropna().unique(),
    default=df["accident_severity"].dropna().unique()
)

# Weather filter
weather_filter = st.sidebar.multiselect(
    "Weather Condition",
    options=df["weather_conditions"].dropna().unique(),
    default=df["weather_conditions"].dropna().unique()
)

# Year filter
if "year" in df.columns:
    year_filter = st.sidebar.slider(
        "Year Range",
        int(df["year"].min()),
        int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max()))
    )
else:
    year_filter = None

# Top N filter
top_n = st.sidebar.selectbox("Top N Categories", [5, 10, 15], index=0)

# FILTER DATA
filtered_df = df[
    (df["accident_severity"].isin(severity_filter)) &
    (df["weather_conditions"].isin(weather_filter))
]

if year_filter:
    filtered_df = filtered_df[filtered_df["year"].between(year_filter[0], year_filter[1])]

# Key Performance Indicators
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Accidents", f"{len(filtered_df):,}")

fatal_count = len(filtered_df[filtered_df["accident_severity"] == "Fatal"])
col2.metric("Fatal Accidents", f"{fatal_count:,}")

avg_vehicle_age = filtered_df["age_of_vehicle"].mean()
col3.metric(
    "Avg Vehicle Age",
    f"{avg_vehicle_age:.1f}" if pd.notnull(avg_vehicle_age) else "N/A"
)

if "vehicle_type" in filtered_df.columns:
    col4.metric("Unique Vehicle Types", filtered_df["vehicle_type"].nunique())
else:
    col4.metric("Unique Vehicle Types", "N/A")

st.markdown("---")

# CHARTS
col_left, col_right = st.columns(2)

# Weather Chart
with col_left:
    st.subheader("Accidents by Weather Condition")

    weather_counts = filtered_df["weather_conditions"].value_counts().head(top_n).reset_index()
    weather_counts.columns = ["weather", "count"]

    fig_weather = px.bar(
        weather_counts,
        x="weather",
        y="count",
        color="weather"
    )

    st.plotly_chart(fig_weather, use_container_width=True)

# Vehicle Age Distribution
with col_right:
    st.subheader("Vehicle Age Distribution")

    if "age_of_vehicle" in filtered_df.columns:
        fig_age = px.histogram(
            filtered_df,
            x="age_of_vehicle",
            nbins=30
        )
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.warning("age_of_vehicle column not found")

# MONTHLY TREND
st.subheader("Accidents by Month")

if "month" in filtered_df.columns:
    monthly = filtered_df.groupby("month").size().reset_index(name="count")

    fig_month = px.line(
        monthly,
        x="month",
        y="count",
        markers=True
    )

    st.plotly_chart(fig_month, use_container_width=True)
else:
    st.warning("month column not found")

# SEVERITY PIE CHART
st.subheader("Accident Severity Distribution")

severity_counts = filtered_df["accident_severity"].value_counts().reset_index()
severity_counts.columns = ["severity", "count"]

fig_severity = px.pie(
    severity_counts,
    names="severity",
    values="count"
)

st.plotly_chart(fig_severity, use_container_width=True)

# MAP
if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
    st.subheader("Accident Locations Map")

    map_df = filtered_df[["latitude", "longitude"]].dropna()

    if not map_df.empty:
        st.map(map_df)
    else:
        st.warning("No valid map data available")

# DOWNLOAD BUTTON
st.markdown("---")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_accidents.csv",
    mime="text/csv"
)

# KEY INSIGHT
st.info(
    "Key Insight: Analysis shows that most accidents occur during weather conditions,"
    "suggesting that driver behavior plays a more significant role than environment factors."
    "Older vehicles also show higher involvement, indicating that potential safety risks associated"
    "with vehicle age." 
)

st.markdown("---")

# FOOTER
st.caption(
    "Data Source: UK Department for Transport via Kaggle (Tsiaras, Road Safety Accidents and Vehicles)"
)