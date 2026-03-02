import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import ast

st.set_page_config(layout="wide")

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
# 🌱 Green Cloud Carbon-Risk Simulation Laboratory
### Real Workload + Real Carbon Intensity + Monte Carlo Risk Evaluation
---
""")

# ==========================================================
# DATA LOADING
# ==========================================================

@st.cache_data
def load_google():
    df = pd.read_csv("google_sample_small.csv")

    df["minute"] = (df["time"] / 1e6 / 60).astype(int)
    df["minute"] -= df["minute"].min()
    df = df[df["minute"] < 1440]

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
    df = df.set_index("Datetime").resample("1min").ffill()
    return df["Actual"].values[:1440]


workload = load_google()
carbon = load_carbon()

# ==========================================================
# SIDEBAR CONTROLS
# ==========================================================

st.sidebar.header("⚙ Simulation Parameters")

servers = st.sidebar.slider("Number of Servers",1,10,3)
runs = st.sidebar.slider("Monte Carlo Runs",50,300,150)
util_threshold = st.sidebar.slider("Utilization Threshold",0.6,0.95,0.85)
carbon_percentile = st.sidebar.slider("Carbon Spike Percentile",60,95,75)

run_btn = st.sidebar.button("🚀 Run Simulation")

TOTAL_CAPACITY = servers * 1.0
CARBON_THRESHOLD = np.percentile(carbon, carbon_percentile)

# ==========================================================
# SIMULATION FUNCTION
# ==========================================================

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

            if strategy=="Carbon-Aware" and carbon[t] > CARBON_THRESHOLD:
                cpu *= 0.75

            elif strategy=="Renewable-Aware" and carbon[t] < CARBON_THRESHOLD:
                cpu *= 1.05

            elif strategy=="CRI-Aware":
                if carbon[t] > CARBON_THRESHOLD and util > 0.5:
                    cpu *= 0.6

            util = cpu / TOTAL_CAPACITY

            power = (100 + 200*util) * 1.4
            energy = power / 60
            total_emission += energy * carbon[t] / 1000

            if cpu > TOTAL_CAPACITY:
                sla += 1

            if util > util_threshold:
                overload += 1

        emissions.append(total_emission)
        sla_probs.append(sla/1440)
        overload_probs.append(overload/1440)

    return np.array(emissions), np.array(sla_probs), np.array(overload_probs)

# ==========================================================
# TABS
# ==========================================================

tabs = st.tabs([
"1️⃣ Executive Summary",
"2️⃣ Background & Research Gap",
"3️⃣ Datasets",
"4️⃣ Architecture",
"5️⃣ Mathematical Model",
"6️⃣ Scheduling Strategies",
"7️⃣ Stochastic Framework",
"8️⃣ Live Simulation",
"9️⃣ Emission Distributions",
"🔟 Risk & SLA Analysis",
"1️⃣1️⃣ Key Findings",
"1️⃣2️⃣ Limitations & Future Work"
])

# ==========================================================
# TAB 1 — EXECUTIVE SUMMARY
# ==========================================================

with tabs[0]:
    st.markdown("""
    ## Project Objective
    
    This research evaluates how carbon-aware cloud workload scheduling 
    affects sustainability-performance tradeoffs under real-world conditions.
    
    It integrates:
    - Google 2019 cluster workload trace
    - UK national carbon intensity data
    - Utilization-based power modeling
    - Monte Carlo stochastic simulation
    - Novel Carbon Risk Index (CRI)
    
    The goal is to quantify emission reduction **and** probabilistic SLA risk.
    """)

# ==========================================================
# TAB 2 — BACKGROUND & GAP
# ==========================================================

with tabs[1]:
    st.markdown("""
    ## Background
    
    Data centers contribute significantly to global energy consumption.
    Traditional scheduling focuses on throughput and latency, ignoring carbon variability.
    
    ## Research Gap
    
    Existing works:
    - Minimize average carbon
    - Ignore volatility
    - Assume deterministic workload
    - Do not quantify probabilistic risk
    
    ## Research Question
    
    How does carbon intensity volatility combined with workload stochasticity
    influence emission reduction and SLA risk?
    """)

# ==========================================================
# TAB 3 — DATASETS
# ==========================================================

with tabs[2]:
    st.subheader("Google Workload Trace")
    st.line_chart(workload[:300])

    st.subheader("UK Carbon Intensity")
    st.line_chart(carbon[:300])

    st.markdown("""
    Real-world data ensures trace-driven simulation instead of synthetic assumptions.
    """)

# ==========================================================
# TAB 4 — ARCHITECTURE
# ==========================================================

with tabs[3]:

    fig, ax = plt.subplots(figsize=(10,4))
    ax.axis("off")

    components = [
        "Workload Trace",
        "Scheduler",
        "Utilization Model",
        "Power Model",
        "Carbon Model",
        "Monte Carlo Engine"
    ]

    for i, comp in enumerate(components):
        ax.text(i*2,1,comp,ha="center",bbox=dict(boxstyle="round"))
        if i>0:
            ax.arrow((i*2)-1,1,0.8,0,head_width=0.1)

    st.pyplot(fig)

# ==========================================================
# TAB 5 — MATHEMATICAL MODEL
# ==========================================================

with tabs[4]:
    st.latex(r"P(u)=P_{idle}+(P_{max}-P_{idle})u")
    st.latex(r"Emission=\sum Energy(t)\times CI(t)")
    st.latex(r"SLA=P(Demand>Capacity)")
    st.latex(r"CRI=I(CI>threshold)\times Utilization")

# ==========================================================
# TAB 6 — SCHEDULING STRATEGIES
# ==========================================================

with tabs[5]:
    st.markdown("""
    **Round Robin** – baseline without carbon awareness
    
    **Carbon-Aware** – reduces load during high carbon periods
    
    **Renewable-Aware** – increases load during low carbon periods
    
    **CRI-Aware** – risk-sensitive throttling when both load and carbon spike are high
    """)

# ==========================================================
# TAB 7 — STOCHASTIC FRAMEWORK
# ==========================================================

with tabs[6]:
    st.markdown("""
    CPU demand is modeled as:
    
    CPU_t ~ Normal(mean=trace, std=5%)
    
    Monte Carlo simulation runs multiple independent trials
    to produce probability distributions instead of single outputs.
    """)

# ==========================================================
# TAB 8 — LIVE SIMULATION
# ==========================================================

with tabs[7]:

    if run_btn:

        strategies = ["Round Robin","Carbon-Aware","Renewable-Aware","CRI-Aware"]
        results = {}

        for s in strategies:
            results[s] = simulate(s)

        summary = []
        for s in strategies:
            emissions = results[s][0]
            summary.append({
                "Strategy":s,
                "Mean Emission":emissions.mean(),
                "95% CI ±":stats.sem(emissions)*1.96,
                "SLA Probability":results[s][1].mean(),
                "Overload Probability":results[s][2].mean()
            })

        st.dataframe(pd.DataFrame(summary))
        st.success("Simulation Completed")

# ==========================================================
# TAB 9 — EMISSION DISTRIBUTIONS
# ==========================================================

with tabs[8]:

    if run_btn:
        for s in strategies:
            fig, ax = plt.subplots()
            ax.hist(results[s][0], bins=20)
            ax.set_title(f"{s} Emission Distribution")
            st.pyplot(fig)

# ==========================================================
# TAB 10 — RISK ANALYSIS
# ==========================================================

with tabs[9]:
    st.markdown("""
    SLA violation occurs when demand exceeds capacity.
    
    Overload probability captures stress conditions.
    
    CRI integrates carbon spikes and utilization,
    enabling risk-sensitive sustainability evaluation.
    """)

# ==========================================================
# TAB 11 — KEY FINDINGS
# ==========================================================

with tabs[10]:
    st.markdown("""
    - Carbon-aware reduces emissions.
    - Renewable-aware may increase total energy.
    - Emission depends on both energy and carbon intensity.
    - CRI balances emission reduction and SLA risk.
    - Monte Carlo reveals probabilistic sustainability tradeoffs.
    """)

# ==========================================================
# TAB 12 — LIMITATIONS
# ==========================================================

with tabs[11]:
    st.markdown("""
    ### Limitations
    - One-month carbon dataset
    - Single-region modeling
    - No seasonal variability
    - No workload migration
    
    ### Future Work
    - Multi-region scheduling
    - Seasonal carbon analysis
    - Renewable forecasting integration
    """)
