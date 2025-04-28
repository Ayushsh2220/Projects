import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import connect_db

# ✅ Set page config first
st.set_page_config(page_title="Dashboard", layout="wide")

# 🚫 Block unauthenticated access immediately after page config
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# ✅ Now continue building the page
st.title("Resume Analytics Dashboard")

df = pd.read_sql("SELECT * FROM resumes", connect_db())

col1, col2 = st.columns(2)
col1.metric("Total Resumes", len(df))
col2.metric("Avg Score", round(df['score'].mean(), 2) if not df.empty else "N/A")

st.subheader("Match Score Distribution")
fig = px.histogram(df, x="score", nbins=10, title="Score Distribution")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Skill Frequency")
skill_list = []
df['skills'].dropna().apply(lambda x: skill_list.extend(x.lower().split(", ")))
skill_df = pd.Series(skill_list).value_counts().reset_index()
skill_df.columns = ['Skill', 'Count']
fig2 = px.bar(skill_df.head(10), x='Skill', y='Count', title="Top 10 Skills")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Resume Status Overview")
status_counts = df['status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']
fig3 = px.pie(status_counts, names='Status', values='Count', title="Resume Pipeline")
st.plotly_chart(fig3, use_container_width=True)
