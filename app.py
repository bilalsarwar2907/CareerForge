import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import streamlit as st
import json
from main import analyze_cv
from tools import list_applications, search_jobs, search_jobs_denmark
from rag import index_document, answer_with_rag
from client import call_claude_json
from prompts import MATCH_PROMPT_FINAL

# Index knowledge base on startup
if "indexed" not in st.session_state:
    if os.path.exists("data/knowledge/career_guide.txt"):
        index_document("data/knowledge/career_guide.txt", "Career Guide")
    st.session_state.indexed = True

st.set_page_config(page_title="CareerForge", layout="wide")
st.title("CareerForge")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "CV Analysis", "Job Match", "Job Search", "Applications", "Career Assistant"
])

# Tab 1: CV Analysis
with tab1:
    st.header("Analyze Your CV")
    cv_text = st.text_area("Paste your CV text:", height=300)
    if st.button("Analyze"):
        if cv_text:
            with st.spinner("Analyzing..."):
                result = analyze_cv(cv_text)
            st.subheader("Summary")
            st.write(result.get("summary", ""))
            st.subheader("Skills")
            st.write(", ".join(result.get("skills", [])))
            st.subheader("Recommendations")
            for rec in result.get("recommendations", []):
                st.write(f"• {rec}")
        else:
            st.warning("Please paste your CV text first.")

# Tab 2: Job Match
with tab2:
    st.header("Match CV to Job Description")
    col1, col2 = st.columns(2)
    with col1:
        cv_input = st.text_area("Your CV:", height=200)
    with col2:
        job_input = st.text_area("Job Description:", height=200)

    if st.button("Match"):
        if cv_input and job_input:
            with st.spinner("Matching..."):
                result = call_claude_json(MATCH_PROMPT_FINAL.format(
                    cv_text=cv_input, job_text=job_input
                ))
            score = result.get("score", 0)
            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
            st.markdown(f"### Match Score: :{color}[{score}/100]")
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Strengths")
                for s in result.get("strengths", []):
                    st.write(f"✅ {s}")
            with col4:
                st.subheader("Gaps")
                for g in result.get("gaps", []):
                    st.write(f"❌ {g}")
        else:
            st.warning("Please fill in both fields.")

# Tab 3: Job Search
with tab3:
    st.header("Search Jobs")
    keywords = st.text_input("Keywords:", "Python developer")
    market = st.radio("Market:", ["Denmark (Remote + Boards)", "UK (Adzuna)"], horizontal=True)
    location = st.text_input("Location:", "copenhagen" if "Denmark" in market else "london")
    if st.button("Search"):
        with st.spinner("Searching..."):
            if "Denmark" in market:
                jobs = search_jobs_denmark(keywords, location)
            else:
                jobs = search_jobs(keywords, location)
        if jobs:
            for job in jobs:
                with st.expander(f"{job['title']} — {job['company']}"):
                    st.write(f"📍 {job['location']}")
                    st.write(f"💰 {job['salary']}")
                    if job.get("url"):
                        st.markdown(f"[View Job]({job['url']})")
        else:
            st.info("No jobs found. Try different keywords.")

        if "Denmark" in market:
            st.divider()
            st.markdown("#### 🇩🇰 Search directly on Danish job boards")
            encoded = keywords.replace(" ", "+")
            st.markdown(
                f"- [Jobindex.dk](https://www.jobindex.dk/jobsoegning?q={encoded})\n"
                f"- [Jobnet.dk](https://job.jobnet.dk/CV/FindWork?SearchString={encoded})\n"
                f"- [LinkedIn Denmark](https://www.linkedin.com/jobs/search/?keywords={encoded}&location=Denmark)\n"
                f"- [The Hub (Nordic startups)](https://www.thehub.io/jobs?q={encoded})"
            )

# Tab 4: Application Tracker
with tab4:
    st.header("Application Tracker")
    apps = list_applications()
    if apps:
        st.table(apps)
    else:
        st.info("No applications tracked yet.")

# Tab 5: Career Assistant
with tab5:
    st.header("Career Assistant")
    st.caption("Ask anything about interviews, CVs, or career strategy.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask a career question...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                answer = answer_with_rag(question)
            st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})