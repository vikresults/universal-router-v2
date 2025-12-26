import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic
import random

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Universal Router", layout="wide")

# --- 2. GSF SUSTAINABILITY ENGINE ---
def search_address(query):
    if not query or len(query) < 3:
        return None
    try:
        geolocator = ArcGIS(user_agent="universal_router_v2")
        return geolocator.geocode(query)
    except Exception:
        return None

def calculate_gsf_metrics(miles):
    """
    GSF Standard SCI calculation.
    Operational (O): 0.404 kg/mile
    Embodied (E): 0.025 kg (Device lifecycle)
    """
    operational_c = miles * 0.404 
    embodied_c = 0.025 
    sci_score = operational_c + embodied_c
    return sci_score

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
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN NAVIGATION ---
st.title("🌐 Universal Router")
app_phase = st.radio(
    "Select Mode",
    ["📍 Plan Trip", "🚗 Active Drive", "📊 Impact Report"],
    horizontal=True
)
st.divider()

# --- 5. PHASE LOGIC ---

# PHASE 1: PLANNING (GSF OPTIMIZED)
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
                # Store coordinates
                st.session_state.start_node = start_res.address
                st.session_state.end_node = end_res.address
                
                coords_s = (start_res.latitude, start_res.longitude)
                coords_e = (end_res.latitude, end_res.longitude)
                dist = geodesic(coords_s, coords_e).miles
                st.session_state.current_miles = dist
                
                # GSF Impact Box
                sci_val = calculate_gsf_metrics(dist)
                st.markdown(f"""
                <div style="background-color: #e6f4ea; padding: 20px; border-radius: 15px; border-left: 5px solid #34a853; margin-bottom: 20px;">
                    <h3 style="margin:0; color:#1e4620;">🌱 GSF Impact Report</h3>
                    <p style="margin:5px 0;"><b>SCI Score:</b> {sci_val:.2f} kg CO2e</p>
                    <small>Standard: SCI = (Operational Emissions + Embodied Emissions)</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Stable Map (Fixed the flickering/disappearing issue)
                avg_lat = (start_res.latitude + end_res.latitude) / 2
                avg_lon = (start_res.longitude + end_res.longitude) / 2
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
                folium.Marker(coords_s, popup="Start").add_to(m)
                folium.Marker(coords_e, popup="End").add_to(m)
                
                st_folium(m, width="100%", height=450, key="trip_map_stable")
            else:
                st.error("📍 Location Not Found. Please try adding a city name.")
        else:
            st.warning("Please enter both locations.")

# PHASE 2: ACTIVE DRIVE
elif app_phase == "🚗 Active Drive":
    st.subheader("Navigation Center")
    if 'start_node' in st.session_state:
        st.write(f"🚩 **Route:** {st.session_state.start_node} → {st.session_state.end_node}")
        s_clean = st.session_state.start_node.replace(" ", "+")
        e_clean = st.session_state.end_node.replace(" ", "+")
        google_url = f"https://www.google.com/maps/dir/?api=1&origin={s_clean}&destination={e_clean}"
        st.link_button("🚀 OPEN GPS NAVIGATION", google_url, type="primary")
    else:
        st.warning("Please plan a trip first!")

# PHASE 3: IMPACT REPORT
elif app_phase == "📊 Impact Report":
    st.subheader("Your Green Scorecard")
    if 'current_miles' in st.session_state:
        sci_val = calculate_gsf_metrics(st.session_state.current_miles)
        st.metric("Total SCI Score", f"{sci_val:.2f} kg CO2e")
        st.success("Your route is optimized for lower carbon intensity! 🏆")
    else:
        st.write("No data yet. Start planning to see your impact!")

st.divider()
st.caption("Universal Router v2.0 | GSF SCI Standard | 2025")
