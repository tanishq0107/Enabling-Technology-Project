import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🌱 Green Cloud Computing Simulation Dashboard")
st.subheader("Stochastic Carbon-Risk-Aware Workload Scheduling")

# =====================================================
# SECTION 1 – PROBLEM STATEMENT
# =====================================================

st.header("1️⃣ Problem Statement")

st.write("""
Modern cloud data centers consume massive electricity and contribute
significantly to global carbon emissions. Traditional schedulers optimize
performance and utilization but ignore carbon volatility and emission risks.

This project investigates how workload scheduling strategies affect:

- Total CO₂ emissions
- SLA violation probability
- System overload probability
- Carbon spike exposure
""")

# =====================================================
# SECTION 2 – DATASETS USED
# =====================================================

st.header("2️⃣ Datasets Used")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Workload Dataset")
    st.write("""
    - Google 2019 Cluster Sample
    - Real CPU task requests
    - Minute-level aggregation
    """)

with col2:
    st.subheader("🌍 Carbon Intensity Dataset")
    st.write("""
    - UK National Grid (1 month)
    - Actual carbon intensity (gCO2/kWh)
    - Minute-level resampling
    """)

# =====================================================
# SECTION 3 – SYSTEM ARCHITECTURE
# =====================================================

st.header("3️⃣ System Architecture")

st.write("""
Simulation Flow:

1. Load real workload data (CPU demand per minute)
2. Load real carbon intensity data
3. Apply scheduling strategy
4. Compute utilization
5. Calculate power consumption
6. Calculate emissions
7. Compute probabilistic metrics
8. Run Monte Carlo (100 runs)
""")

# =====================================================
# SECTION 4 – MATHEMATICAL MODEL
# =====================================================

st.header("4️⃣ Mathematical Model")

st.latex(r"P(u) = P_{idle} + (P_{max} - P_{idle}) \cdot u")
st.latex(r"Emission(t) = Energy(t) \times CarbonIntensity(t)")
st.latex(r"SLA = P(CPU_{demand} > Capacity)")
st.latex(r"CRI = I(CI > threshold) \times Utilization")

# =====================================================
# SECTION 5 – SCHEDULING STRATEGIES
# =====================================================

st.header("5️⃣ Scheduling Strategies")

st.markdown("""
- **Round Robin** – Baseline scheduling
- **Carbon-Aware** – Reduce load during high-carbon periods
- **Renewable-Aware** – Increase load during low-carbon periods
- **CRI-Aware (Proposed)** – Reduce load when carbon spike risk × utilization exceeds threshold
""")

# =====================================================
# SECTION 6 – SIMULATION PARAMETERS
# =====================================================

st.header("6️⃣ Simulation Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    num_servers = st.slider("Number of Servers", 1, 20, 3)

with col2:
    monte_runs = st.slider("Monte Carlo Runs", 10, 200, 100)

with col3:
    util_threshold = st.slider("Utilization Threshold", 0.5, 1.0, 0.85)

# =====================================================
# SECTION 7 – SIMULATED RESULTS (Your Actual Results)
# =====================================================

st.header("7️⃣ Results Summary")

data = {
    "Strategy": ["Round Robin", "Carbon-Aware", "Renewable-Aware", "CRI-Aware"],
    "Expected Emission": [922.85, 901.07, 932.35, 916.78],
    "SLA Probability": [0.0104, 0.0090, 0.0118, 0.0083],
    "Overload Probability": [0.0184, 0.0155, 0.0195, 0.0150]
}

df = pd.DataFrame(data)
st.dataframe(df)

# =====================================================
# SECTION 8 – RESULTS VISUALIZATION
# =====================================================

st.header("8️⃣ Emission Comparison")

fig, ax = plt.subplots()
ax.bar(df["Strategy"], df["Expected Emission"])
ax.set_ylabel("Expected CO2 Emission")
plt.xticks(rotation=30)
st.pyplot(fig)

st.header("9️⃣ SLA Violation Probability")

fig2, ax2 = plt.subplots()
ax2.bar(df["Strategy"], df["SLA Probability"])
ax2.set_ylabel("SLA Probability")
plt.xticks(rotation=30)
st.pyplot(fig2)

# =====================================================
# SECTION 10 – KEY FINDINGS
# =====================================================

st.header("🔟 Key Findings")

st.write("""
✅ Carbon-Aware scheduling achieved lowest emissions  
❌ Renewable-Aware increased total emissions  
⚖️ CRI-Aware balanced emission reduction and SLA stability  
📉 Carbon intensity optimization alone does not guarantee emission reduction  
📊 Trade-off exists between sustainability and performance  
""")

# =====================================================
# SECTION 11 – CARBON RISK INDEX CONTRIBUTION
# =====================================================

st.header("1️⃣1️⃣ Novel Contribution – Carbon Risk Index")

st.write("""
CRI models carbon spike risk weighted by system utilization.
Unlike pure carbon-aware scheduling, CRI accounts for system stress.

This enables:
- Risk-sensitive emission control
- Balanced SLA performance
- Selective workload reduction
""")

# =====================================================
# SECTION 12 – WHAT THIS PROJECT DEMONSTRATES
# =====================================================

st.header("1️⃣2️⃣ What This Project Demonstrates")

st.write("""
1. Workload-carbon interaction is non-linear.
2. Increasing computation during renewable periods may increase total emissions.
3. Carbon-aware scheduling is more effective than renewable amplification.
4. Risk-based scheduling balances sustainability and performance.
5. Monte Carlo evaluation is essential for robust sustainability modeling.
""")

# =====================================================
# SECTION 13 – LIMITATIONS
# =====================================================

st.header("1️⃣3️⃣ Limitations")

st.write("""
- Only one month of carbon data used
- No seasonal variability modeled
- No geographical multi-region simulation
- No real workload migration modeling
""")

# =====================================================
# SECTION 14 – FUTURE WORK
# =====================================================

st.header("1️⃣4️⃣ Future Work")

st.write("""
- Multi-region carbon-aware scheduling
- Seasonal carbon analysis
- Integration with renewable forecasting
- Workload migration modeling
""")

# =====================================================
# SECTION 15 – CONCLUSION
# =====================================================

st.header("1️⃣5️⃣ Conclusion")

st.write("""
This project presents a stochastic, data-driven simulation framework
for evaluating carbon-aware scheduling in cloud data centers.

It demonstrates that carbon intensity optimization alone is insufficient,
and risk-sensitive scheduling provides better sustainability-performance trade-offs.
""")

st.success("Dashboard Generated Successfully 🚀")