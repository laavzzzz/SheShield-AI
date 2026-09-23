import streamlit as st
import json

def init_user_session():
    """Initializes user profile state in Streamlit session."""
    if "user" not in st.session_state:
        st.session_state.user = {
            "is_logged_in": False,
            "name": "",
            "email": "",
            "age": None,
            "default_location": "",
            "location_permission": True
        }

def render_login_and_onboarding():
    init_user_session()
    
    if not st.session_state.user["is_logged_in"]:
        st.subheader("🛡️ Welcome to SheShield AI")
        st.info("Sign in to access personalized safety monitoring and location alerts.")
        
        # Simplified Google Login simulation/integration
        if st.button("🔐 Sign in with Google"):
            # Replace with streamlit-google-auth in production
            st.session_state.user["is_logged_in"] = True
            st.session_state.user["name"] = "Verified User"
            st.session_state.user["email"] = "user@example.com"
            st.rerun()
            
    # First time profile completion if age missing
    elif st.session_state.user["is_logged_in"] and not st.session_state.user["age"]:
        st.subheader("📋 Complete Your Safety Profile")
        with st.form("profile_form"):
            age = st.number_input("Age", min_value=12, max_value=100, value=22)
            default_loc = st.text_input("Home City / Region (Fallback location)")
            submitted = st.form_submit_button("Save Profile")
            
            if submitted:
                st.session_state.user["age"] = age
                st.session_state.user["default_location"] = default_loc
                st.success("Profile saved!")
                st.rerun()