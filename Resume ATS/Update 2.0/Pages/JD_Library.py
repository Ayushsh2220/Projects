import streamlit as st
import os
import json

st.set_page_config(page_title="Job Description Library", layout="wide")
st.title("JD Library")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

JD_DIR = "jd_templates"
os.makedirs(JD_DIR, exist_ok=True)

st.subheader("Create New JD Template")
template_name = st.text_input("Template Name")
jd_text = st.text_area("Job Description Content", height=250)

if st.button("Save Template"):
    if template_name:
        with open(os.path.join(JD_DIR, f"{template_name}.json"), "w") as f:
            json.dump({"jd": jd_text}, f)
        st.success(f"{template_name} saved!")
    else:
        st.warning("Template name required")

st.subheader("View Existing Templates")
files = [f for f in os.listdir(JD_DIR) if f.endswith(".json")]
for f_name in files:
    with open(os.path.join(JD_DIR, f_name)) as f:
        data = json.load(f)
    st.markdown(f"### {f_name.replace('.json', '')}")
    st.code(data['jd'], language='markdown')
