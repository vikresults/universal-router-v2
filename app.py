import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. APP CONFIG & STYLING (The "Uber" Look) ---
st.set_page_config(page_title="Universal Router", layout="wide")

st.markdown("""
    <style>
    /* Uber-style Black and Blue Theme */
    .stApp { background-color: #ffffff; color: #000000; }
    .stButton > button {
        width: 100%; border-radius: 30px; height: 55px;
        background-color: #000000; color: white; border: none;
        font-size: 18px; font-weight: bold; transition: 0.3s;
    }
    .stButton > button:hover { background-color: #276EF1; color: white; }
    
    /* Green Metric Card Styling */
    .green-card {
        background-color: #e6f4ea;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #34a853;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FEATURE TOGGLES (Your Mentor-Requested Switch) ---
if 'ENABLE_GSF_METRICS' not in st.session_state:
    st.session_state.ENABLE_GSF_METRICS = True

# --- 3. THE SUSTAINABILITY ENGINE ---
def get_green_impact(miles_saved):
    # Standard: 404 grams of CO2 per mile (EPA avg)
    kg_co2 = miles_saved * 0.404
    
    # Funny "Sustainability Reward" Logic
    if kg_co2 > 10:
        reward = "🚀 You saved enough CO2 to binge-watch 3 seasons of a show in 4K!"
    elif kg_co2 > 5:
        reward = "☕ That's equivalent to making 150 cups of coffee guilt-free!"
    else:
        reward = "📱 You saved enough energy to charge your phone for a whole year!"
    return kg_co2, reward

# --- 4. MAIN UI ---
st.title("🌐 Universal Router")
st.caption("Global Logistics | Sustainable Routing | Mobile-First")

# Display the Green Dashboard if toggled ON
if st.session_state.ENABLE_GSF_METRICS:
    st.markdown("### 🌱 Sustainability Dashboard (GSF Standard)")
    
    # Placeholder for calculation (we will link this to the actual route later)
    simulated_miles_saved = 15.5 
    kg_saved, funny_fact = get_green_impact(simulated_miles_saved)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SCI Score (CO2 Saved)", f"{kg_saved:.2f} kg")
    with col2:
        st.info(funny_fact)
    
    st.divider()

st.write("### 🚗 Start Your Global Route")
# We will add the Location Search and Map in the next step!
