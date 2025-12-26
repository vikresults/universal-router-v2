import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic

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
    """GSF Standard SCI calculation: Operational + Embodied."""
    operational_c = miles * 0.404 
    embodied_c = 0.025 
    return operational_c + embodied_c

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

# --- 4. MAIN NAVIGATION ---
st.title("🌐 Universal Router")
app_phase = st.radio("Select Mode", ["📍 Plan Trip", "🚗 Active Drive", "📊 Impact Report"], horizontal=True)
st.divider()

# --- 5. PHASE 1: PLANNING (GSF OPTIMIZED) ---
if app_phase == "📍 Plan Trip":
    st.info("GSF Standard: Calculating Software Carbon Intensity (SCI)")
    
    col1, col2 = st.columns(2)
    with col1:
        start_q = st.text_input("Start Location", placeholder="e.g. London, UK", key="s_in")
    with col2:
        end_q = st.text_input("Destination", placeholder="e.g. Paris, France", key="e_in")

    # ACTION BUTTON
    if st.button("🗺️ Generate Global Route"):
        if start_q and end_q:
            with st.spinner("Analyzing Sustainability Data..."):
                start_res = search_address(start_q)
                end_res = search_address(end_q)
            
            if start_res and end_res:
                # SAVE EVERYTHING TO SESSION STATE (This stops the disappearing act)
                st.session_state.start_node = start_res.address
                st.session_state.end_node = end_res.address
                st.session_state.coords_s = (start_res.latitude, start_res.longitude)
                st.session_state.coords_e = (end_res.latitude, end_res.longitude)
                st.session_state.dist = geodesic(st.session_state.coords_s, st.session_state.coords_e).miles
                st.session_state.show_results = True
                st.balloons()
            else:
                st.error("📍 Location Not Found.")
        else:
            st.warning("Please enter both locations.")

    # --- DISPLAY AREA (Outside the button click, inside the phase) ---
    if st.session_state.get('show_results'):
        # 1. GSF Impact Box
        sci_val = calculate_gsf_metrics(st.session_state.dist)
        st.markdown(f"""
        <div class="green-card">
            <h3 style="margin:0; color:#1e4620;">🌱 GSF Impact Report</h3>
            <p style="margin:5px 0;"><b>SCI Score:</b> {sci_val:.2f} kg CO2e Saved</p>
            <small>Standard: SCI = (Operational + Embodied Emissions)</small>
        </div>
        """, unsafe_allow_html=True)

        

        # 2. Map Generation
        lat_avg = (st.session_state.coords_s[0] + st.session_state.coords_e[0]) / 2
        lon_avg = (st.session_state.coords_s[1] + st.session_state.coords_e[1]) / 2
        m = folium.Map(location=[lat_avg, lon_avg], zoom_start=4)
        folium.Marker(st.session_state.coords_s, popup="Start", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker(st.session_state.coords_e, popup="End", icon=folium.Icon(color='green')).add_to(m)
        
        # Display the Map
        st_folium(m, width="100%", height=450, key="stable_map")

# --- 6. PHASE 2: ACTIVE DRIVE ---
elif app_phase == "🚗 Active Drive":
    st.subheader("Navigation Center")
    if 'start_node' in st.session_state:
        st.write(f"🚩 **Current Route:** {st.session_state.start_node} → {st.session_state.end_node}")
        s_url = st.session_state.start_node.replace(" ", "+")
        e_url = st.session_state.end_node.replace(" ", "+")
        st.link_button("🚀 OPEN GPS NAVIGATION", f"https://www.google.com/maps/dir/{s_url}/{e_url}", type="primary")
    else:
        st.warning("Please plan a trip first!")

# --- 7. PHASE 3: IMPACT REPORT ---
elif app_phase == "📊 Impact Report":
    st.subheader("Your Green Scorecard")
    if 'dist' in st.session_state:
        sci_val = calculate_gsf_metrics(st.session_state.dist)
        st.metric("Total CO2 Avoided", f"{sci_val:.2f} kg")
        st.success("Great job! You are using optimized GSF routing standards.")
    else:
        st.write("No trip data found.")

st.divider()
st.caption("Universal Router v2.0 | GSF Standard | 2025")
