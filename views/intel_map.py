import streamlit as st
import folium
from folium import plugins 
from streamlit_folium import st_folium
import pandas as pd

# ==========================================
# 1. ENTERPRISE CSS
# ==========================================
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #0E1117;
                color: gray;
                text-align: center;
                padding: 10px;
                font-size: 12px;
                border-top: 1px solid #333;
                z-index: 100;
            }
            </style>
            <div class="footer">
                <p><b>TerraGuard AI Enterprise</b> | Developed for Multimedia University (MMU) | Geospatial Engine</p>
            </div>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🗺️ Geospatial Intelligence & Risk Map")
st.write("Live meteorological analysis, active threat monitoring, and community reports.")
st.markdown("---")

# ==========================================
# 2. CHECK FOR LIVE ALERTS
# ==========================================
if 'live_emergency' in st.session_state:
    emergency = st.session_state['live_emergency']
    st.error(f"🚨 **ACTIVE ESCALATION IN PROGRESS:** Units responding to {emergency['location']}!")

# ==========================================
# 3. DASHBOARD LAYOUT
# ==========================================
col1, col2 = st.columns([1.2, 2.5])

with col1:
    st.subheader("🌤️ Meteorological Parameters")
    
    temperature = st.slider("Ambient Temp (°C)", 20, 45, 32)
    humidity = st.slider("Rel. Humidity (%)", 10, 100, 60)
    wind_speed = st.slider("Wind Velocity (km/h)", 0, 50, 15)

    risk_level = "Low"
    risk_color = "green"
    radius_size = 2000

    if temperature > 35 and humidity < 30:
        risk_level = "Extreme"
        risk_color = "red"
        radius_size = 5000
    elif temperature > 30 and humidity < 50:
        risk_level = "High"
        risk_color = "orange"
        radius_size = 4000
    elif temperature > 25 and humidity < 70:
        risk_level = "Moderate"
        risk_color = "orange" 
        radius_size = 3000

    st.markdown("### **System Threat Level:**")
    st.markdown(f"<div style='background-color:{risk_color}; padding:10px; border-radius:5px; text-align:center;'><span style='color:white; font-size: 24px; font-weight:bold;'>{risk_level.upper()}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 📋 Live Activity Log")
    # Base Data
    log_data = pd.DataFrame({
        "Time": ["11:02 PM", "10:45 PM", "09:30 PM"],
        "Sector": ["Ayer Keroh", "Bukit Beruang", "Cyberjaya"],
        "Status": ["Investigating", "Cleared", "Cleared"]
    })
    
    # If there is a live emergency, add it to the top of the log!
    if 'live_emergency' in st.session_state:
        new_event = pd.DataFrame({
            "Time": ["JUST NOW"],
            "Sector": [st.session_state['live_emergency']['location']],
            "Status": [st.session_state['live_emergency']['status']]
        })
        log_data = pd.concat([new_event, log_data], ignore_index=True)
        
    st.dataframe(log_data, use_container_width=True, hide_index=True)

with col2:
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Drone Sensors", "14 / 15", "93% Grid Coverage")
    m2.metric("Community Reports", "2 Pending", "-1 from yesterday", delta_color="inverse")
    m3.metric("Network Status", "Stable 🟢")
    
    center_lat, center_lon = 2.2794, 102.2967
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB dark_matter")
    
    plugins.LocateControl(
        auto_start=False, 
        strings={"title": "Acquire Operator GPS Coordinates", "popup": "Operator Location"}
    ).add_to(m)

    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_size,
        color=risk_color,
        fill=True,
        fill_color=risk_color,
        fill_opacity=0.3,
        tooltip=f"Calculated Threat Zone: {risk_level}"
    ).add_to(m)

    # If there is a live emergency, plot a massive red marker!
    if 'live_emergency' in st.session_state:
        folium.Marker(
            [st.session_state['live_emergency']['lat'], st.session_state['live_emergency']['lon']],
            popup=f"<b>Status:</b> {st.session_state['live_emergency']['status']}<br><b>Location:</b> {st.session_state['live_emergency']['location']}",
            tooltip="🔥 LIVE ESCALATION EVENT",
            icon=folium.Icon(color="darkred", icon="fire")
        ).add_to(m)
    else:
        # Default mock markers if no live emergency
        folium.Marker(
            [2.2850, 102.3000],
            popup="<b>Status:</b> Investigating Smoke<br><b>Log:</b> Sector 7",
            tooltip="⚠️ Priority 3 Alert",
            icon=folium.Icon(color="orange", icon="cloud")
        ).add_to(m)

    st_folium(m, width=850, height=450)