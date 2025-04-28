import streamlit as st
import pandas as pd
from datetime import datetime
from utils.recruiter_db import register_user
from utils.db import connect_db

st.set_page_config(page_title="Admin Tools", layout="wide")
st.title("🛠️ Admin Control Panel")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# 🚫 Block unauthorized roles
if st.session_state['role'] != 'admin':
    st.error("⛔ Access denied. Admins only.")
    st.stop()

# ✅ User registration
st.subheader("🔐 Create Recruiter/Admin Account")
with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username")
        email = st.text_input("Email")
    with col2:
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["recruiter", "admin"])
    if st.form_submit_button("➕ Register User"):
        if username and password and email:
            success = register_user(username, password, email, role)
            st.success(f"{role.capitalize()} created!" if success else "Username already exists.")
        else:
            st.warning("Please fill in all fields.")

st.markdown("---")

# ✅ Resume management with filtering
conn = connect_db()
df = pd.read_sql("SELECT * FROM resumes", conn)

st.subheader("📊 Filter Resumes")

if not df.empty:
    # ✅ Only Score filtering now
    df['score'] = df['score'] * 100  # 🆕 Convert to percentage
    min_score, max_score = df['score'].min(), df['score'].max()

    score_range = st.slider(
        "📈 Match Score Range (%)",
        float(min_score),
        float(max_score),
        (float(min_score), float(max_score))
    )

    filtered_df = df[
        (df['score'] >= score_range[0]) &
        (df['score'] <= score_range[1])
    ]
else:
    filtered_df = df

# ✅ Download filtered resumes
st.subheader("⬇️ Download Filtered Resumes")
if not filtered_df.empty:
    st.download_button(
        "📄 Download CSV",
        filtered_df.to_csv(index=False),
        file_name="filtered_resumes.csv",
        mime='text/csv'
    )
else:
    st.info("No resumes match the selected filters.")

# ✅ Single Resume Deletion
st.markdown("---")
st.subheader("❌ Delete a Resume")
if not filtered_df.empty:
    resume_to_delete = st.selectbox("Select Resume", filtered_df['name'].tolist())
    if st.button("🧹 Delete Selected Resume"):
        conn.execute("DELETE FROM resumes WHERE name = ?", (resume_to_delete,))
        conn.commit()
        st.success(f"✅ Resume '{resume_to_delete}' deleted.")
        st.rerun()

else:
    st.info("No resumes available to delete.")

# ✅ Full reset
st.markdown("---")
st.subheader("🚨 Reset Resume Database")
if st.button("⚠️ Delete All Resumes"):
    conn.execute("DELETE FROM resumes")
    conn.commit()
    st.success("🧨 All resumes deleted!")
    st.rerun()

