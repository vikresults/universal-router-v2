import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic
import random

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Universal Router", layout="wide")

# --- 2. THE SUSTAINABILITY ENGINE ---
def search_address(query):
    if not query or len(query) < 3:
        return None
    try:
        geolocator = ArcGIS(user_agent="universal_router_v2")
        return geolocator.geocode(query)
    except Exception:
        return None
def calculate_gsf_metrics(miles):
    """GSF Standard SCI calculation."""
    operational_c = miles * 0.404 
    embodied_c = 0.025 
    sci_score = operational_c + embodied_c
    return sci_score
def get_green_impact(miles_saved):
    # Standard: 404 grams of CO2 per mile (EPA avg)
    kg_co2 = miles_saved * 0.404
    if kg_co2 > 10:
        reward = "🚀 You saved enough CO2 to binge-watch 3 seasons of a show in 4K!"
    elif kg_co2 > 5:
        reward = "☕ That's equivalent to making 150 cups of coffee guilt-free!"
    else:
        reward = "📱 You saved enough energy to charge your phone for a whole year!"
    return kg_co2, reward

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .stButton > button {
        width: 100%; border-radius: 30px; height: 55px;
        background-color: #000000; color: white; border: none;
        font-size: 18px; font-weight: bold; transition: 0.3s;
    }
    .stButton > button:hover { background-color: #276EF1; color: white; }
    .green-card {
        background-color: #e6f4ea; padding: 20px; border-radius: 15px;
        border-left: 5px solid #34a853; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN UI & NAVIGATION ---
st.title("🌐 Universal Router")

app_phase = st.radio(
    "Select Mode",
    ["📍 Plan Trip", "🚗 Active Drive", "📊 Impact Report"],
    horizontal=True
)

st.divider()

# --- 5. APP PHASES ---

# PHASE 1: PLANNING
if app_phase == "📍 Plan Trip":
   st.info("GSF Standard: Calculating Software Carbon Intensity (SCI)")
    
    col1, col2 = st.columns(2)
    with col1:
        start_q = st.text_input("Start Location", placeholder="e.g. London, UK", key="s_in")
    with col2:
        end_q = st.text_input("Destination", placeholder="e.g. Paris, France", key="e_in")

    if st.button("🗺️ Generate Global Route"):
        if start_q and end_q:
            with st.spinner("Analyzing Route Sustainability..."):
                start_res = search_address(start_q)
                end_res = search_address(end_q)
            
            if start_res and end_res:
                st.session_state.start_node = start_res.address
                st.session_state.end_node = end_res.address
                
                coords_s = (start_res.latitude, start_res.longitude)
                coords_e = (end_res.latitude, end_res.longitude)
                dist = geodesic(coords_s, coords_e).miles
                st.session_state.current_miles = dist
                
                # --- GSF IMPACT BOX ---
                sci_val = calculate_gsf_metrics(dist)
                st.markdown(f"""
                <div style="background-color: #e6f4ea; padding: 20px; border-radius: 15px; border-left: 5px solid #34a853; margin-bottom: 20px;">
                    <h3 style="margin:0; color:#1e4620;">🌱 GSF Impact Report</h3>
                    <p style="margin:5px 0;"><b>SCI Score:</b> {sci_val:.2f} kg CO2e</p>
                    <small>Standard: SCI = (Operational Emissions + Embodied Emissions)</small>
                </div>
                """, unsafe_allow_html=True)
                
                
                
                # --- STABLE MAP ---
                avg_lat = (start_res.latitude + end_res.latitude) / 2
                avg_lon = (start_res.longitude + end_res.longitude) / 2
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
                folium.Marker(coords_s, popup="Start").add_to(m)
                folium.Marker(coords_e, popup="End").add_to(m)
                
                # 'key' stops the map from disappearing!
                st_folium(m, width="100%", height=450, key="trip_map")
            else:
                st.error("📍 Location Not Found.")
elif app_phase == "🚗 Active Drive":
    st.subheader("Navigation Center")
    if 'start_node' in st.session_state:
        st.write(f"**From:** {st.session_state.start_node}")
        st.write(f"**To:** {st.session_state.end_node}")
        
        # Link button to GPS
        start_clean = st.session_state.start_node.replace(" ", "+")
        end_clean = st.session_state.end_node.replace(" ", "+")
        google_url = f"https://www.google.com/maps/dir/?api=1&origin={start_clean}&destination={end_clean}"
        st.link_button("🚀 OPEN GPS NAVIGATION", google_url, type="primary")
    else:
        st.warning("Please plan a trip first in the 'Plan Trip' tab!")

# PHASE 3: IMPACT REPORT
elif app_phase == "📊 Impact Report":
    st.subheader("Your Green Scorecard")
    if 'current_miles' in st.session_state:
        kg_saved, reward = get_green_impact(st.session_state.current_miles)
        st.metric("CO2 Avoided", f"{kg_saved:.2f} kg")
        st.success(reward)
    else:
        st.write("No data available yet. Start planning to see your impact!")

st.divider()
st.caption("Global Logistics | Sustainable Routing | Mobile-First | 2025")
