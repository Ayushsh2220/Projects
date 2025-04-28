import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db import connect_db

st.set_page_config(page_title="Review & Update Resumes", layout="wide")
st.title("📋 Review & Update Resumes")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# ✅ Connect to DB
conn = connect_db()
df = pd.read_sql("SELECT * FROM resumes", conn)

# ✅ Convert dates
if 'upload_date' in df.columns:
    df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')

# ✅ Filters
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    name_filter = st.text_input("🔎 Search by Name")
with col2:
    skill_filter = st.text_input("🛠️ Search by Skill")
with col3:
    status_filter = st.selectbox(
        "🔖 Filter by Status",
        options=["All", "Pending", "Shortlisted", "Interviewed", "Rejected"],
        index=0
    )

# ✅ Score range slider
st.subheader("📈 Score Range & 📅 Upload Date Filters")

if not df.empty:
    min_score, max_score = df['score'].min(), df['score'].max()
    if min_score == max_score:
        min_score = max(0, min_score - 5)
        max_score = min(100, max_score + 5)

    score_range = st.slider(
        "Select Match Score Range (%)",
        min_value=float(min_score),
        max_value=float(max_score),
        value=(float(min_score), float(max_score))
    )

    min_date = df['upload_date'].min()
    max_date = df['upload_date'].max()

    if pd.isna(min_date) or pd.isna(max_date):
        min_date = datetime.today()
        max_date = datetime.today()

    date_range = st.date_input(
        "Select Upload Date Range",
        (min_date, max_date)
    )
else:
    score_range = (0, 100)
    date_range = (datetime.today(), datetime.today())

# ✅ Apply all filters
if name_filter:
    df = df[df['name'].str.contains(name_filter, case=False, na=False)]
if skill_filter:
    df = df[df['skills'].str.contains(skill_filter, case=False, na=False)]
if status_filter != "All":
    df = df[df['status'] == status_filter]
if not df.empty:
    df = df[
        (df['score'] * 100 >= score_range[0]) &
        (df['score'] * 100 <= score_range[1]) &
        (df['upload_date'].dt.date >= date_range[0]) &
        (df['upload_date'].dt.date <= date_range[1])
    ]

# ✅ Display Resumes
st.markdown("---")

if not df.empty:
    for _, row in df.iterrows():
        score_percentage = row['score'] * 100

        # Color based on score
        if score_percentage >= 85:
            badge_color = "green"
            match_label = "Excellent Match"
        elif 70 <= score_percentage < 85:
            badge_color = "orange"
            match_label = "Good Match"
        else:
            badge_color = "red"
            match_label = "Low Match"

        upload_date_display = row['upload_date'].strftime('%Y-%m-%d') if pd.notna(row['upload_date']) else "N/A"
        last_updated_display = row['last_updated'] if 'last_updated' in row and pd.notna(row['last_updated']) else "N/A"

        # ✅ Stylish resume card
        with st.container():
            st.markdown(f"""
            <div style='padding:15px; border:1px solid #ccc; border-radius:12px; margin-bottom:12px; background-color:#f9f9f9'>
                <h4 style='margin-bottom:5px;'>
                    {row['name']} | 
                    <a href="mailto:{row['email']}" style='text-decoration:none;'>{row['email']}</a> 
                    <span style='background-color:{badge_color}; color:white; padding:5px 10px; border-radius:20px; font-size:14px; margin-left:8px;'>{score_percentage:.2f}% - {match_label}</span>
                </h4>
                <p style='font-size:13px; color:gray; margin-top:-10px;'>
                    📅 Uploaded: {upload_date_display} &nbsp;&nbsp; 🛠️ Last Updated: {last_updated_display}
                </p>
            """, unsafe_allow_html=True)

            with st.expander("🔎 View Resume Details"):
                st.markdown("### 🛠 Skills")
                st.write(row['skills'])

                st.markdown("### 💼 Experience")
                st.write(row['experience'])

                st.markdown("### 🎓 Education")
                st.write(row['education'])

                required_skills = st.text_input(
                    "Required Skills (comma-separated)", key=f"req_{row['id']}"
                )
                if required_skills:
                    existing = set(row['skills'].lower().split(", "))
                    required = set([s.strip().lower() for s in required_skills.split(",")])
                    missing = required - existing
                    if missing:
                        st.warning(f"⚠️ Missing Skills: {', '.join(missing)}")
                    else:
                        st.success("✅ All required skills are matched!")

                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "Shortlisted", "Interviewed", "Rejected"],
                    index=["Pending", "Shortlisted", "Interviewed", "Rejected"].index(
                        row['status'] if row['status'] else "Pending"
                    ),
                    key=f"status_{row['id']}"
                )
                new_notes = st.text_area(
                    "Recruiter Notes",
                    value=row['notes'] or "",
                    key=f"note_{row['id']}"
                )

                if st.button("💾 Save Updates", key=f"save_{row['id']}"):
                    conn.execute(
                        "UPDATE resumes SET status=?, notes=?, last_updated=? WHERE id=?",
                        (new_status, new_notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), row['id'])
                    )
                    conn.commit()
                    st.success("✅ Resume updated successfully.")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("ℹ️ No resumes found with current filters.")
