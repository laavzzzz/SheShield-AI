import streamlit as st
from streamlit_folium import st_folium
import folium

def render_location_and_map():
    st.sidebar.markdown("### 📍 Location Privacy Controls")
    
    # Toggle button for location status
    location_on = st.sidebar.toggle(
        "Share Live Location with SheShield AI", 
        value=st.session_state.user.get("location_permission", True)
    )
    
    st.session_state.user["location_permission"] = location_on
    
    coords = None
    
    if location_on:
        st.sidebar.caption("🟢 Location Sharing Active")
        
        # Default coordinates (e.g., fallback or default city)
        default_lat, default_lon = 20.2961, 85.8245 # Example: Bhubaneswar
        
        # Render Interactive Folium Map
        m = folium.Map(location=[default_lat, default_lon], zoom_start=14)
        
        # Add User Location Marker
        folium.Marker(
            [default_lat, default_lon],
            popup="Your Current Position",
            tooltip="You are here",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(m)
        
        st.subheader("🗺️ Live Safety Map")
        map_data = st_folium(m, height=300, width=700)
        
        coords = {"lat": default_lat, "lon": default_lon}
    else:
        st.sidebar.caption("🔴 Location Sharing Disabled")
        st.info("🔒 SheShield AI is operating in Anonymous Mode. No location context is sent to the LLM.")
        
    return coords