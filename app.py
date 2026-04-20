import streamlit as st
from agent import get_response
import uuid
from datetime import datetime
import requests

# 🔧 PAGE CONFIG
st.set_page_config(page_title="SheShield AI", page_icon="🛡️", layout="wide")

# 🧠 SESSION INIT
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.current_chat = cid
    st.session_state.chat_sessions[cid] = []

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_location" not in st.session_state:
    st.session_state.user_location = "Unknown"

# 🎨 UI
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fde2e4, #fdf2f8);
}
.user-msg {
    background: linear-gradient(135deg, #d6336c, #f783ac);
    color: white;
    padding: 12px 16px;
    border-radius: 20px 20px 5px 20px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
}
.bot-msg {
    background: white;
    padding: 12px 16px;
    border-radius: 20px 20px 20px 5px;
    margin: 8px 0;
    max-width: 70%;
    border: 1px solid #f1c0c7;
}
.time {
    font-size: 11px;
    opacity: 0.6;
}
.high {color:red;font-weight:bold;}
.medium {color:orange;font-weight:bold;}
.low {color:green;font-weight:bold;}
.stButton>button {
    border-radius: 14px;
    background: #f783ac;
    color: white;
    border: none;
}
.stButton>button:hover {
    background: #d6336c;
}
</style>
""", unsafe_allow_html=True)

# 🧠 SIDEBAR
with st.sidebar:
    st.title("🛡️ SheShield")
    st.caption("Always here for you 💖")

    # 👤 Profile
    st.markdown("### 👤 Profile")
    name = st.text_input("Your Name", st.session_state.user_name)
    st.session_state.user_name = name

    st.markdown("---")

    # 🚨 SOS
    if st.button("🚨 Emergency SOS"):
        st.error("📞 Call 112 NOW!")

    # ➕ New Chat
    if st.button("➕ New Chat"):
        cid = str(uuid.uuid4())
        st.session_state.current_chat = cid
        st.session_state.chat_sessions[cid] = []

    st.markdown("### 💬 Chats")
    for i, cid in enumerate(st.session_state.chat_sessions.keys()):
        if st.button(f"Chat {i+1}"):
            st.session_state.current_chat = cid

    st.markdown("---")

    # 🧰 SAFETY TOOLS
    st.markdown("### 🧰 Safety Tools")

    # 📍 LOCATION (UPGRADED)
    with st.expander("📍 Share Location"):

        st.markdown("### 🌍 Auto Detect Location")
        if st.button("Detect My Location"):
            try:
                res = requests.get("https://ipinfo.io/json").json()
                city = res.get("city", "")
                region = res.get("region", "")
                country = res.get("country", "")
                loc = res.get("loc", "0,0")

                lat, lon = map(float, loc.split(","))

                st.success(f"📍 {city}, {region}, {country}")
                st.map({"lat": [lat], "lon": [lon]})

                st.session_state.user_location = f"{city}, {region}, {country}"

            except:
                st.error("Could not detect location")

        st.markdown("---")

        st.markdown("### 📌 Enter Exact Location")
        lat = st.number_input("Latitude", value=20.5937)
        lon = st.number_input("Longitude", value=78.9629)

        st.map({"lat": [lat], "lon": [lon]})
        st.session_state.user_location_manual = f"{lat}, {lon}"

    # ⚖️ Legal Help
    with st.expander("⚖️ Legal Help"):
        st.write("""
        **Your Rights in India:**
        - You can file FIR at any police station (Zero FIR allowed)
        - Harassment & stalking are punishable offenses
        - Police must assist women immediately
        - You can record evidence legally

        📞 Women Helpline: 1091
        """)

    # 💖 Emotional Support
    with st.expander("💖 Quick Emotion Regulation"):
        st.write("""
        You are not alone 💖

        Try this:
        - Inhale (4 sec)
        - Hold (4 sec)
        - Exhale (6 sec)

        You're safe. You're strong.
        """)

# 🏷️ HEADER
st.title("🛡️ SheShield AI")

if st.session_state.user_name:
    st.caption(f"You are safe, {st.session_state.user_name}. I'm here for you 💖")
else:
    st.caption("Stay aware. Stay safe. You're not alone.")

# 💬 CHAT
messages = st.session_state.chat_sessions[st.session_state.current_chat]

for msg in messages:
    time = msg.get("time", "")
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}<div class='time'>{time}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>{msg['content']}<div class='time'>{time} · 🛡️ Verified</div></div>", unsafe_allow_html=True)

# 📝 INPUT
user_input = st.chat_input("Tell SheShield what's on your mind…")

# 🚀 MAIN LOGIC
if user_input:
    now = datetime.now().strftime("%H:%M")

    messages.append({"role": "user", "content": user_input, "time": now})

    history = "\n".join([m["content"] for m in messages])

    # 🧠 Include location
    location = st.session_state.get("user_location", "Unknown")

    with st.spinner("🧠 Thinking..."):
        result = get_response(
            user_input + f"\nUser Location: {location}",
            history
        )

    answer = result["answer"]
    risk = result["risk"]

    if risk == "HIGH":
        st.progress(100)
        st.markdown("<p class='high'>🚨 HIGH RISK</p>", unsafe_allow_html=True)
    elif risk == "MEDIUM":
        st.progress(60)
        st.markdown("<p class='medium'>⚠️ MEDIUM RISK</p>", unsafe_allow_html=True)
    else:
        st.progress(30)
        st.markdown("<p class='low'>✅ LOW RISK</p>", unsafe_allow_html=True)

    messages.append({"role": "assistant", "content": answer, "time": now})

    st.rerun()