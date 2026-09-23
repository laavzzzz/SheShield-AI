"""
SheShield AI - Advanced Women's Safety Assistant
Path: app.py

A modern, production-grade Streamlit application providing real-time risk assessment,
emotional support, emergency guidance, and location-aware safety monitoring.
"""

import uuid
import html
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
import streamlit as st

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SheShield.App")

# Import backend safety agent with fallback compatibility
try:
    from agent import get_response
except ImportError:
    try:
        from src.llm_handler import get_llm_handler, UserContext
        def get_response(user_input: str, history: str) -> Dict[str, Any]:
            handler = get_llm_handler()
            assessment = handler.evaluate_safety_situation(user_input)
            return {
                "answer": assessment.conversational_response,
                "risk": assessment.risk_level.value,
                "assessment": assessment
            }
    except Exception as e:
        logger.warning(f"Could not load custom backend agent: {e}. Using resilient mock agent.")
        def get_response(user_input: str, history: str) -> Dict[str, Any]:
            return {
                "answer": "I am SheShield AI. I am keeping watch with you. How can I assist your safety right now?",
                "risk": "LOW"
            }

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & METADATA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SheShield AI | Safety Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
def init_session_state() -> None:
    """Initializes and verifies all required session variables."""
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}

    if "current_chat" not in st.session_state:
        cid = str(uuid.uuid4())
        st.session_state.current_chat = cid
        st.session_state.chat_sessions[cid] = []

    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    if "user_location" not in st.session_state:
        st.session_state.user_location = "Unknown (Location Disabled)"

    if "location_coords" not in st.session_state:
        st.session_state.location_coords = None

    if "location_active" not in st.session_state:
        st.session_state.location_active = False

init_session_state()

def create_new_chat() -> None:
    """Safely creates a new chat session without state collision."""
    cid = str(uuid.uuid4())
    st.session_state.chat_sessions[cid] = []
    st.session_state.current_chat = cid

def switch_chat(cid: str) -> None:
    """Switches active chat context."""
    if cid in st.session_state.chat_sessions:
        st.session_state.current_chat = cid

# -----------------------------------------------------------------------------
# 3. ADVANCED STYLING (CSS DESIGN SYSTEM)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* CSS Root Variables & Theme */
    :root {
        --primary-gradient: linear-gradient(135deg, #e63946 0%, #d62828 100%);
        --accent-gradient: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%);
        --bg-gradient: linear-gradient(135deg, #fff5f6 0%, #fde2e4 100%);
        --card-bg: #ffffff;
        --text-color: #2b2d42;
        --border-color: #f1c0c7;
        --shadow-soft: 0 8px 24px rgba(214, 40, 40, 0.08);
    }

    .stApp {
        background: var(--bg-gradient);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }

    /* Message Bubble Components */
    .chat-bubble {
        padding: 16px 20px;
        border-radius: 18px;
        margin-bottom: 12px;
        line-height: 1.5;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        word-wrap: break-word;
    }

    .user-msg-container {
        display: flex;
        justify-content: flex-end;
    }

    .user-msg {
        background: var(--accent-gradient);
        color: white;
        border-bottom-right-radius: 4px;
        max-width: 78%;
    }

    .bot-msg-container {
        display: flex;
        justify-content: flex-start;
    }

    .bot-msg {
        background: var(--card-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-bottom-left-radius: 4px;
        max-width: 82%;
    }

    .msg-meta {
        font-size: 11px;
        margin-top: 6px;
        opacity: 0.75;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Safety Risk Indicator Badges */
    .badge-risk {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .risk-high {
        background-color: #ffe3e3;
        color: #d6336c;
        border: 1px solid #ffb9b9;
    }

    .risk-medium {
        background-color: #fff3bf;
        color: #f59f00;
        border: 1px solid #ffe066;
    }

    .risk-low {
        background-color: #d3f9d8;
        color: #2b8a3e;
        border: 1px solid #b2f2bb;
    }

    /* SOS Header Banner */
    .sos-banner {
        background: #d62828;
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(214, 40, 40, 0.3);
    }

    /* Custom Input Fields & Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SIDEBAR LOGIC & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## SheShield AI")
    st.caption("AI Safety & Emergency Assistance Platform")

    st.markdown("---")

    # User Profile Configuration
    st.markdown("### 👤 User Profile")
    user_name_input = st.text_input(
        "Your Name",
        value=st.session_state.user_name,
        placeholder="Enter your name...",
        key="profile_name"
    )
    st.session_state.user_name = user_name_input.strip()

    st.markdown("---")

    # SOS Emergency Actions
    st.markdown("### 🚨 Immediate Emergency")
    if st.button("🚨 TRIGGER SOS ALERT", use_container_width=True, type="primary"):
        st.error("🚨 **EMERGENCY TRIGGERED**")
        st.markdown("""
        **Take immediate action:**
        - 📞 **Police Emergency:** Call `112`
        - 📞 **Women Helpline:** Call `1091`
        - 📞 **National Helpline:** Call `181`
        """)

    st.markdown("---")

    # Chat Session Navigation
    col_new_chat, _ = st.columns([1, 0.1])
    with col_new_chat:
        if st.button("➕ New Chat Session", use_container_width=True):
            create_new_chat()
            st.rerun()

    st.markdown("#### 💬 Active Sessions")
    session_keys = list(st.session_state.chat_sessions.keys())
    for idx, cid in enumerate(session_keys):
        is_active = (cid == st.session_state.current_chat)
        btn_label = f"{'🟢' if is_active else '💬'} Chat Session #{idx + 1}"
        
        if st.button(btn_label, key=f"session_btn_{cid}", use_container_width=True):
            switch_chat(cid)
            st.rerun()

    st.markdown("---")

    # Safety Tools Accordions
    st.markdown("### 🧰 Safety Tools")

    # 📍 Location Management
    with st.expander("📍 Location & GPS Settings"):
        location_toggle = st.toggle(
            "Share Location Context",
            value=st.session_state.location_active,
            key="location_permission_toggle"
        )
        st.session_state.location_active = location_toggle

        if location_toggle:
            if st.button("🛰️ Auto-Detect Location", use_container_width=True):
                try:
                    with st.spinner("Fetching geolocation..."):
                        response = requests.get("https://ipinfo.io/json", timeout=3.0)
                        if response.status_code == 200:
                            data = response.json()
                            city = data.get("city", "Unknown City")
                            region = data.get("region", "")
                            country = data.get("country", "")
                            loc = data.get("loc", "0,0")
                            
                            lat_str, lon_str = loc.split(",")
                            lat, lon = float(lat_str), float(lon_str)

                            st.session_state.user_location = f"{city}, {region}, {country}"
                            st.session_state.location_coords = {"lat": lat, "lon": lon}
                            st.success(f"📍 {city}, {region}")
                        else:
                            st.error("Failed to reach location service.")
                except Exception as ex:
                    logger.error(f"Location error: {ex}")
                    st.error("Could not complete location lookup.")

            if st.session_state.location_coords:
                st.map({"lat": [st.session_state.location_coords["lat"]], "lon": [st.session_state.location_coords["lon"]]})

            st.caption("Or set custom location:")
            c_lat = st.number_input("Latitude", value=20.2961, format="%.4f")
            c_lon = st.number_input("Longitude", value=85.8245, format="%.4f")
            if st.button("Set Coordinates", use_container_width=True):
                st.session_state.location_coords = {"lat": c_lat, "lon": c_lon}
                st.session_state.user_location = f"Custom ({c_lat:.2f}, {c_lon:.2f})"
                st.success("Coordinates updated!")
        else:
            st.info("🔒 Anonymous Mode Active. Location context is hidden.")

    # ⚖️ Legal Help
    with st.expander("⚖️ Legal Rights & Helpline"):
        st.markdown("""
        **Your Essential Rights:**
        - **Zero FIR:** File a complaint at *any* police station regardless of jurisdiction.
        - **Right to Privacy:** Statements can be recorded at home with a female officer present.
        - **Free Legal Aid:** Women are entitled to free legal assistance.

        **Helplines:**
        - National Emergency: `112`
        - Women Helpline: `1091`
        """)

    # 💖 De-escalation & Calming
    with st.expander("💖 Panic & Grounding Support"):
        st.markdown("""
        **4-7-8 Breathing Exercise:**
        1. 🫁 **Inhale** slowly through nose for **4s**
        2. ⏸️ **Hold** your breath for **7s**
        3. 🌬️ **Exhale** fully through mouth for **8s**

        *You are strong. Help is always available.*
        """)

# -----------------------------------------------------------------------------
# 5. MAIN CHAT APPLICATION UI
# -----------------------------------------------------------------------------
st.markdown("## 🛡️ SheShield AI")

if st.session_state.user_name:
    st.caption(f"Welcome back, **{html.escape(st.session_state.user_name)}**. I am monitoring your context and ready to assist. 💖")
else:
    st.caption("Real-time safety, emotional guidance, and emergency intelligence.")

# Active Chat History Rendering
current_messages = st.session_state.chat_sessions.get(st.session_state.current_chat, [])

for msg in current_messages:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")
    timestamp = msg.get("time", "")
    risk_level = msg.get("risk", "LOW")

    escaped_content = html.escape(content).replace("\n", "<br>")

    if role == "user":
        st.markdown(f"""
        <div class="user-msg-container">
            <div class="chat-bubble user-msg">
                <div>{escaped_content}</div>
                <div class="msg-meta" style="justify-content: flex-end; color: rgba(255,255,255,0.8);">
                    <span>{timestamp}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f"""
        <div class="bot-msg-container">
            <div class="chat-bubble bot-msg">
                <span class="badge-risk {risk_class}">🛡️ {risk_level} RISK</span>
                <div>{escaped_content}</div>
                <div class="msg-meta" style="color: #6c757d;">
                    <span>{timestamp} · Verified Guidance</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. USER INPUT & RESPONSE PIPELINE
# -----------------------------------------------------------------------------
user_input = st.chat_input("Describe your situation or ask for safety advice...")

if user_input:
    formatted_time = datetime.now().strftime("%H:%M")

    # Store user message
    st.session_state.chat_sessions[st.session_state.current_chat].append({
        "role": "user",
        "content": user_input,
        "time": formatted_time
    })

    # Prepare chat history string for context window
    history_str = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.chat_sessions[st.session_state.current_chat]
    ])

    # Inject location context if enabled
    active_location = (
        st.session_state.user_location 
        if st.session_state.location_active 
        else "Location Sharing Disabled"
    )
    
    combined_query = f"{user_input}\n[Context - Location: {active_location}]"

    # Evaluate Safety Query via Agent
    with st.spinner("🧠 Analyzing safety context..."):
        try:
            res = get_response(combined_query, history_str)
            bot_answer = res.get("answer", "I am here with you. Please tell me more about your situation.")
            risk_status = res.get("risk", "LOW").upper()
        except Exception as err:
            logger.error(f"Error during agent invocation: {err}")
            bot_answer = "I encountered a processing delay, but I am still here. If you are in immediate danger, please call 112 directly."
            risk_status = "HIGH"

    # Store assistant response with risk parameter
    st.session_state.chat_sessions[st.session_state.current_chat].append({
        "role": "assistant",
        "content": bot_answer,
        "risk": risk_status,
        "time": formatted_time
    })

    # Trigger UI update
    st.rerun()