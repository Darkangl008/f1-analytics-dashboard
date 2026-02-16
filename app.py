import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------- SETUP ---------- #

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

st.set_page_config(layout="wide")
st.title("🏎️ Ultimate F1 Analytics Dashboard")

# ---------- SIDEBAR ---------- #

st.sidebar.header("🏁 Race Selection")

year = st.sidebar.selectbox("Year", [2024, 2023, 2022])
gp = st.sidebar.text_input("Grand Prix", "Monaco")
session_type = st.sidebar.selectbox("Session", ["R", "Q"])

load = st.sidebar.button("Load Race Data")

# ---------- LOAD SESSION ---------- #

@st.cache_data(show_spinner=False)
def load_session(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session

if load:
    with st.spinner("Loading race data..."):
        st.session_state.session = load_session(year, gp, session_type)

# ---------- MAIN APP ---------- #

if "session" in st.session_state:

    session = st.session_state.session
    st.success("Race data loaded ✅")

    drivers = session.laps['Driver'].unique()

    col1, col2 = st.columns(2)

    with col1:
        driver1 = st.selectbox("Driver A", drivers)

    with col2:
        remaining = [d for d in drivers if d != driver1]
        driver2 = st.selectbox("Driver B", remaining)

    lap1 = session.laps.pick_driver(driver1).pick_fastest()
    lap2 = session.laps.pick_driver(driver2).pick_fastest()

    tel1 = lap1.get_telemetry()
    tel2 = lap2.get_telemetry()

    # ---------- KPI CARDS ---------- #

    st.header("⚡ Lap Summary")

    t1 = lap1["LapTime"].total_seconds()
    t2 = lap2["LapTime"].total_seconds()

    faster = driver1 if t1 < t2 else driver2
    diff = abs(t1 - t2)

    st.markdown(f"### 🏆 {faster} faster by **{diff:.2f}s**")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(f"{driver1} Lap", f"{t1:.2f}s")
    col2.metric(f"{driver2} Lap", f"{t2:.2f}s")
    col3.metric("Top Speed A", f"{tel1['Speed'].max():.0f} km/h")
    col4.metric("Top Speed B", f"{tel2['Speed'].max():.0f} km/h")

    # ---------- SPEED COMPARISON ---------- #

    st.header("📈 Speed Comparison")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(tel1["Distance"], tel1["Speed"], label=driver1)
    ax.plot(tel2["Distance"], tel2["Speed"], label=driver2)
    ax.set_xlabel("Lap Distance")
    ax.set_ylabel("Speed (km/h)")
    ax.legend()
    st.pyplot(fig)

    # ---------- LIVE DELTA ---------- #

    st.header("⏱️ Time Delta (Who is ahead on track)")

    delta, ref_tel, comp_tel = fastf1.utils.delta_time(lap1, lap2)

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(ref_tel["Distance"], delta)
    ax2.set_ylabel("Time Difference (s)")
    ax2.set_xlabel("Distance")
    ax2.axhline(0)
    st.pyplot(fig2)

    # ---------- TRACK MAP ---------- #

    st.header("🗺️ Track Map — Speed Colored")

    x = tel1["X"]
    y = tel1["Y"]
    speed = tel1["Speed"]

    fig3, ax3 = plt.subplots(figsize=(6, 6))
    sc = ax3.scatter(x, y, c=speed, cmap="viridis", s=3)
    ax3.axis("equal")
    plt.colorbar(sc, label="Speed")
    st.pyplot(fig3)

    # ---------- CORNER vs STRAIGHT ---------- #

    st.header("🧠 Driving Style Analysis")

    avg_throttle1 = tel1["Throttle"].mean()
    avg_throttle2 = tel2["Throttle"].mean()

    if avg_throttle1 > avg_throttle2:
        st.write(f"🚀 {driver1} was more aggressive on throttle")
    else:
        st.write(f"🚀 {driver2} was more aggressive on throttle")

else:
    st.info("👈 Select race details and click 'Load Race Data'")
