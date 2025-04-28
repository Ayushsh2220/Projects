import streamlit as st
import json
import os
import pandas as pd
from utils.db import connect_db
from sentence_transformers import SentenceTransformer, util

# ✅ Page setup
st.set_page_config(page_title="Reverse JD Matching", layout="wide")
st.title("🔁 Reverse Match: Resume ➜ JD")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# ✅ Load BERT model once and cache it
@st.cache_resource(show_spinner="Loading BERT model...")
def load_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

model = load_model()

# ✅ Load resume data from DB
conn = connect_db()
resumes = pd.read_sql("SELECT id, name, file_name FROM resumes", conn)

# ✅ Load JD templates
JD_DIR = "jd_templates"
jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".json")]

# ✅ UI selections
selected_resume = st.selectbox("📄 Select Resume", resumes['name'].tolist())
selected_jd = st.selectbox("📝 Select JD Template", [f.replace(".json", "") for f in jd_files])

# ✅ Matching logic
if st.button("🔍 Match Now"):
    resume_row = resumes[resumes['name'] == selected_resume].iloc[0]

    # Fetch resume text from DB (combined fields)
    resume_text = conn.execute("""
        SELECT experience || ' ' || education || ' ' || skills 
        FROM resumes 
        WHERE id = ?
    """, (resume_row['id'],)).fetchone()[0]

    # Load JD content
    with open(os.path.join(JD_DIR, f"{selected_jd}.json"), "r", encoding="utf-8") as f:
        jd_text = json.load(f).get("jd", "")

    # BERT-based score calculation
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    score = util.cos_sim(resume_emb, jd_emb).item()

    # Display result
    st.success(f"✅ Match Score with **{selected_jd}** JD: `{score*100:.2f}`")
