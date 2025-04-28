import streamlit as st

st.set_page_config(page_title="Interview Scheduler", layout="wide")
st.title("Interview Scheduling")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

st.markdown("""
This module can be integrated with:
- **Google Calendar API** (OAuth2.0)  
- **Microsoft Outlook API**

**Use case:**  
- Auto-schedule interviews  
- Send invites to candidates  
- Show availability slots
""")

st.info("This section is currently a placeholder. Let me know when you're ready to integrate OAuth/calendar APIs.")
