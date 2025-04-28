import streamlit as st
import pandas as pd
from utils.parser import process_resume_file
from utils.db import insert_resume, init_db
from sentence_transformers import SentenceTransformer
from datetime import datetime

# ✅ Page setup
st.set_page_config(page_title="Upload Resumes", layout="wide")
st.title("📄 Upload & Parse Resumes")

# 🚫 Block unauthenticated access
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# ✅ Initialize database
init_db()

# ✅ Load BERT model once
@st.cache_resource(show_spinner="Loading BERT Model...")
def load_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

model = load_model()

# ✅ Input fields
st.subheader("📝 Job Description")
job_description = st.text_area("Paste your Job Description here", height=150)

st.subheader("📤 Upload Resumes")
uploaded_files = st.file_uploader(
    "Upload Resume files (.pdf, .docx)", 
    type=["pdf", "docx"], 
    accept_multiple_files=True
)

# ✅ Main processing logic
if uploaded_files and job_description:
    st.subheader("⏳ Processing Resumes...")

    upload_results = []  # 🆕 Collect results here

    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):
            try:
                result = process_resume_file(file, job_description, model)
                insert_resume(file.name, result)

                score_percentage = result['score'] * 100
                upload_date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 🆕 Capture upload time

                if score_percentage >= 85:
                    color = "green"
                    label = "Excellent Match"
                elif 70 <= score_percentage < 85:
                    color = "orange"
                    label = "Good Match"
                else:
                    color = "red"
                    label = "Low Match"

                # ✅ Append result for summary table
                upload_results.append({
                    "Resume": file.name,
                    "Score (%)": round(score_percentage, 2),
                    "Match Quality": label,
                    "Upload Date": upload_date_now  # 🆕 Include Upload Date
                })

                # ✅ Show individual upload result
                st.markdown(f"""
                <div style='padding:12px; border:1px solid #ccc; border-radius:10px; margin-bottom:12px; background-color:#f9f9f9'>
                    <strong>✅ {file.name}</strong><br>
                    <span style='background-color:{color}; padding:5px 10px; border-radius:12px; color:white; font-size:14px;'>
                        Score: {score_percentage:.2f}% ({label})
                    </span><br>
                    <small>📅 Uploaded: {upload_date_now}</small>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Failed to process **{file.name}**: {e}")

    # ✅ After all uploads, show a summary table
    if upload_results:
        st.markdown("---")
        st.subheader("📋 Upload Summary Table")

        summary_df = pd.DataFrame(upload_results)
        summary_df = summary_df.sort_values(by="Score (%)", ascending=False)  # Sort by best matches
        st.dataframe(summary_df, use_container_width=True)

        # ✅ Allow Download of Upload Summary
        st.download_button(
            label="📥 Download Upload Summary as CSV",
            data=summary_df.to_csv(index=False),
            file_name="upload_summary.csv",
            mime="text/csv"
        )

else:
    if uploaded_files and not job_description:
        st.warning("⚠️ Please paste a Job Description before processing.")
    elif job_description and not uploaded_files:
        st.warning("⚠️ Please upload at least one resume file to continue.")
