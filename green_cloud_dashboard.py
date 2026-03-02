import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

st.set_page_config(layout="wide")

# ===============================
# PREMIUM HEADER
# ===============================

st.markdown("""
# 🌱 Green Cloud Carbon-Risk Simulation Lab
### Real Workload + Real Carbon + Stochastic Monte Carlo Framework
---
""")

# ===============================
# DATA LOADING
# ===============================

import ast

@st.cache_data
def load_google():
    df = pd.read_csv("google_sample_small.csv")

    # Convert timestamp to minute index
    df["minute"] = (df["time"] / 1e6 / 60).astype(int)
    df["minute"] -= df["minute"].min()
    df = df[df["minute"] < 1440]

    # Extract CPU value from resource_request column
    def extract_cpu(x):
        try:
            d = ast.literal_eval(x)
            return float(d.get("cpus", 0))
        except:
            return 0

    df["cpu"] = df["resource_request"].apply(extract_cpu)

    cpu_series = df.groupby("minute")["cpu"].sum().reindex(range(1440), fill_value=0)

    return cpu_series.values

@st.cache_data
def load_carbon():
    df = pd.read_csv("Carbon_Intensity_Data.csv")
    df.columns = ["Datetime","Actual","Forecast","Index"]
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.set_index("Datetime").resample("1T").ffill()
    return df["Actual"].values[:1440]

workload = load_google()
carbon = load_carbon()

# ===============================
# SIDEBAR CONTROLS
# ===============================

st.sidebar.header("⚙ Simulation Controls")

servers = st.sidebar.slider("Servers",1,10,3)
runs = st.sidebar.slider("Monte Carlo Runs",50,300,150)
util_threshold = st.sidebar.slider("Utilization Threshold",0.6,0.95,0.85)
carbon_percentile = st.sidebar.slider("Carbon Spike Percentile",60,95,75)

run_btn = st.sidebar.button("🚀 Run Simulation")

TOTAL_CAPACITY = servers * 1.0
CARBON_THRESHOLD = np.percentile(carbon, carbon_percentile)

# ===============================
# SIMULATION FUNCTION
# ===============================

def simulate(strategy):

    emissions, sla_probs, overload_probs = [], [], []

    for _ in range(runs):

        total_emission = 0
        sla = 0
        overload = 0

        for t in range(1440):

            cpu = np.random.normal(workload[t], workload[t]*0.05)
            cpu = max(cpu,0)

            util = cpu / TOTAL_CAPACITY

            if strategy=="Carbon-Aware" and carbon[t]>CARBON_THRESHOLD:
                cpu *= 0.75
            elif strategy=="Renewable-Aware" and carbon[t]<CARBON_THRESHOLD:
                cpu *= 1.05
            elif strategy=="CRI-Aware":
                if carbon[t]>CARBON_THRESHOLD and util>0.5:
                    cpu *= 0.6

            util = cpu / TOTAL_CAPACITY

            power = (100 + 200*util)*1.4
            energy = power/60
            total_emission += energy*carbon[t]/1000

            if cpu > TOTAL_CAPACITY:
                sla +=1
            if util > util_threshold:
                overload +=1

        emissions.append(total_emission)
        sla_probs.append(sla/1440)
        overload_probs.append(overload/1440)

    return np.array(emissions), np.array(sla_probs), np.array(overload_probs)

# ===============================
# TABS
# ===============================

tabs = st.tabs([
"Executive Summary",
"Background & Gap",
"Datasets",
"Architecture",
"Mathematical Model",
"Scheduling Strategies",
"Stochastic Framework",
"Live Simulation",
"Emission Distributions",
"Risk & SLA Analysis",
"Key Findings",
"Limitations & Future Work"
])

# --------------------------------
# EXECUTIVE SUMMARY
# --------------------------------
with tabs[0]:
    st.markdown("""
    ### What This Project Does
    This simulation evaluates how cloud workload scheduling strategies 
    impact carbon emissions under real carbon intensity volatility.

    It combines:
    - Real Google workload traces
    - Real UK grid carbon intensity
    - Utilization-based power modeling
    - Monte Carlo stochastic evaluation
    - Novel Carbon Risk Index (CRI)
    """)

# --------------------------------
# ARCHITECTURE DIAGRAM
# --------------------------------
with tabs[3]:

    st.markdown("### Interactive System Architecture")

    fig, ax = plt.subplots(figsize=(10,4))
    ax.axis('off')

    components = [
        "Google Workload Data",
        "Scheduler",
        "Utilization Model",
        "Power Model",
        "Carbon Model",
        "Monte Carlo Engine"
    ]

    for i,comp in enumerate(components):
        ax.text(i*2,1,comp,ha='center',bbox=dict(boxstyle="round"))
        if i>0:
            ax.arrow((i*2)-1,1,0.8,0,head_width=0.1)

    st.pyplot(fig)

    st.write("""
    The system processes workload and carbon data sequentially to compute
    emission outputs under multiple scheduling policies.
    """)

# --------------------------------
# MATHEMATICAL MODEL
# --------------------------------
with tabs[4]:
    st.latex(r"P(u) = P_{idle} + (P_{max}-P_{idle})u")
    st.latex(r"Emission = \sum Energy(t) \cdot CI(t)")
    st.latex(r"SLA = P(Demand > Capacity)")
    st.latex(r"CRI = I(CI>threshold) \times Utilization")

# --------------------------------
# LIVE SIMULATION
# --------------------------------
with tabs[7]:

    if run_btn:

        strategies = ["Round Robin","Carbon-Aware","Renewable-Aware","CRI-Aware"]
        results = {}

        for s in strategies:
            results[s] = simulate(s)

        summary = []
        for s in strategies:
            emissions = results[s][0]
            mean = emissions.mean()
            ci = stats.sem(emissions)*1.96
            summary.append({
                "Strategy":s,
                "Mean Emission":mean,
                "95% CI ±":ci,
                "Mean SLA":results[s][1].mean(),
                "Mean Overload":results[s][2].mean()
            })

        st.dataframe(pd.DataFrame(summary))
        st.success("Simulation Complete")

# --------------------------------
# EMISSION DISTRIBUTIONS
# --------------------------------
with tabs[8]:

    if run_btn:

        for s in strategies:
            fig, ax = plt.subplots()
            ax.hist(results[s][0], bins=20)
            ax.set_title(f"{s} Emission Distribution")
            st.pyplot(fig)

# --------------------------------
# KEY FINDINGS
# --------------------------------
with tabs[10]:

    st.markdown("""
    ### Core Research Insights

    1. Carbon-aware scheduling reduces total emission.
    2. Renewable amplification may increase overall energy.
    3. Emission = Energy × Carbon → non-linear effect.
    4. CRI provides balanced sustainability-performance tradeoff.
    5. Monte Carlo evaluation reveals probabilistic risk exposure.
    """)

# --------------------------------
# LIMITATIONS
# --------------------------------
with tabs[11]:
    st.write("""
    - One-month carbon dataset
    - Single region modeling
    - No workload migration modeling
    - No seasonal variation included

    Future Work:
    - Multi-region carbon-aware scheduling
    - Seasonal variability modeling
    - Live renewable forecasting integration
    """)





