import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic
# ... other imports ...

# --- STEP 4: PASTE HELPER FUNCTIONS HERE ---
def calculate_sci_score(miles_optimized, total_deliveries):
    """GSF Standard SCI calculation."""
    operational_c = miles_optimized * 0.404 
    embodied_c = 0.025 
    sci_score = (operational_c + embodied_c) / total_deliveries
    return sci_score

# --- UI STYLING & APP START ---
st.set_page_config(page_title="Universal Router", layout="wide")
# ... the rest of your app ...
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
# --- STEP 6: PHASE SELECTOR ---
# This acts like the navigation bar at the bottom of Uber/Lyft
app_phase = st.radio(
    "Select Mode",
    ["📍 Plan Trip", "🚗 Active Drive", "📊 Impact Report"],
    horizontal=True
)

st.divider()

# --- PHASE 1: PLANNING ---
if app_phase == "📍 Plan Trip":
    # MOVE ALL YOUR SEARCH & MAP CODE UNDER THIS BLOCK
    # (The inputs start_q, end_q, and the Generate Route button)
    st.info("Search for a destination to see your Green Savings.")
    
    # [All your previous code from Step 5.1 goes here]
    # IMPORTANT: All that code must be INDENTED one level to the right.

# --- PHASE 2: ACTIVE DRIVE ---
elif app_phase == "🚗 Active Drive":
    st.subheader("Navigation Center")
    if 'start_node' in st.session_state:
        st.write(f"**From:** {st.session_state.start_node}")
        st.write(f"**To:** {st.session_state.end_node}")
        
        # Link button to actually launch GPS
        google_url = f"https://www.google.com/maps/dir/?api=1&origin={st.session_state.start_node}&destination={st.session_state.end_node}"
        st.link_button("🚀 OPEN GPS NAVIGATION", google_url, type="primary")
    else:
        st.warning("Please plan a trip first!")

# --- PHASE 3: IMPACT REPORT ---
elif app_phase == "📊 Impact Report":
    st.subheader("Your Green Scorecard")
    if 'current_miles' in st.session_state:
        total_kg = st.session_state.current_miles * 0.404
        st.metric("Carbon Intensity (SCI) Avoided", f"{total_kg:.2f} kg")
        st.success("You are in the top 5% of sustainable drivers this week! 🏆")
    else:
        st.write("No data available yet. Start driving to save carbon!")
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
# --- 5. GLOBAL SEARCH & MAPPING ---
def search_address(query, region="World"):
    """Search for any address globally."""
    try:
        # We use ArcGIS geocoder for high accuracy across all countries
        geolocator = ArcGIS()
        location = geolocator.geocode(query)
        return location
    except Exception as e:
        st.error(f"Search Error: {e}")
        return None

st.write("### 🌍 Global Route Planner")
col_src, col_dst = st.columns(2)

with col_src:
    start_q = st.text_input("Start (City, Address, or Landmark)", placeholder="e.g. Eiffel Tower")
with col_dst:
    end_q = st.text_input("End (City, Address, or Landmark)", placeholder="e.g. London Eye")

# --- THE SEARCH & MAP ACTION AREA ---
if st.button("🗺️ Generate Global Route"):
    # 1. Look up the addresses
    start_res = search_address(start_q)
    end_res = search_address(end_q)
    
    # 2. STEP 5.1: THE SAFETY GATE
    # This checks: "Did we actually find both addresses?"
    if start_res and end_res:
        # --- SUCCESS PATH ---
        st.session_state.start_node = start_res.address
        st.session_state.end_node = end_res.address
        
        # Calculate Real Distance between coordinates
        from geopy.distance import geodesic
        start_coords = (start_res.latitude, start_res.longitude)
        end_coords = (end_res.latitude, end_res.longitude)
        distance_miles = geodesic(start_coords, end_coords).miles
        
        # Update the Session State for the Green Engine
        st.session_state.current_miles = distance_miles
        kg_saved, reward_text = get_green_impact(distance_miles)
        
        # Show the visual celebration
        st.balloons()
        st.success(f"✅ Route Found: {distance_miles:.1f} miles")
        
        # Build the Map
        avg_lat = (start_res.latitude + end_res.latitude) / 2
        avg_lon = (start_res.longitude + end_res.longitude) / 2
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
        folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='black')).add_to(m)
        st_folium(m, width="100%", height=400)
        
        # Show the Green Reward
        st.info(reward_text)
        st.write(f"🌱 Carbon Avoided: {kg_saved:.2f} kg CO2")

    else:
        # --- THE FALLBACK PATH ---
        # If the search failed, we show this instead of crashing
        st.error("📍 Location Not Found. Please check your spelling or try adding a city name (e.g. '123 Main St, New York').")
