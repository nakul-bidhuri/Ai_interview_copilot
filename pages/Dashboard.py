import streamlit as st
import pandas as pd
from pathlib import Path
from database.database import get_dashboard_metrics, get_all_interviews
from utils.pdf_generator import get_pdf_bytes

st.set_page_config(
    page_title="Analytics Dashboard | AI Interview Copilot Pro",
    page_icon="📊",
    layout="wide"
)

# Load CSS
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='main-title'>📊 Candidate Interview Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Track your interview readiness, score trajectory, and performance growth across mock rounds.</div>", unsafe_allow_html=True)

# Fetch stats from SQLite
metrics = get_dashboard_metrics()
interviews = get_all_interviews()

# 4 Key Metrics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card">
          <h3>Total Interviews</h3>
          <h1>{metrics['total_interviews']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
          <h3>Average Score</h3>
          <h1>{metrics['average_score'] if metrics['total_interviews'] > 0 else '—'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
          <h3>Best Score</h3>
          <h1>{metrics['best_score'] if metrics['total_interviews'] > 0 else '—'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="card">
          <h3>PDF Reports</h3>
          <h1>{metrics['total_reports']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.divider()

if not interviews:
    st.info("👋 You haven't completed any mock interviews yet. Head over to the Live Interview Studio to practice your first resume-based interview!")
    if st.button("🚀 Start Your First Interview", type="primary"):
        st.switch_page("pages/Interview.py")
else:
    # Build DataFrame for Analytics
    data = []
    for it in interviews:
        data.append({
            "Date": it["created_at"],
            "Candidate": it["candidate_name"],
            "Role": it["target_role"],
            "Overall Score": it["overall_score"],
            "Grace Years": it["grace_years"],
            "Technical": it.get("scores", {}).get("technical_depth", 8.0),
            "Communication": it.get("scores", {}).get("communication_clarity", 8.0),
            "Confidence": it.get("scores", {}).get("confidence_delivery", 8.0),
            "STAR Alignment": it.get("scores", {}).get("star_method_alignment", 7.5),
            "Problem Solving": it.get("scores", {}).get("problem_solving", 8.0),
        })

    df = pd.DataFrame(data)

    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown("### 📈 Score Progression Over Time")
        chart_df = df.sort_values("Date")
        st.line_chart(chart_df.set_index("Date")[["Overall Score"]], color="#0072ff")

    with chart_col2:
        st.markdown("### 🎯 Competency Comparison")
        latest = df.iloc[0]
        cat_df = pd.DataFrame({
            "Competency": ["Technical", "Communication", "Confidence", "STAR Alignment", "Problem Solving"],
            "Score": [
                latest["Technical"],
                latest["Communication"],
                latest["Confidence"],
                latest["STAR Alignment"],
                latest["Problem Solving"]
            ]
        })
        st.bar_chart(cat_df.set_index("Competency"), color="#10b981")

    st.write("")
    st.markdown("### 🕒 Recent Interview History")

    for it in interviews[:5]:
        with st.expander(f"**{it['target_role']}** | {it['candidate_name']} ({it['created_at']}) — Score: **{it['overall_score']} / 10**"):
            c_det1, c_det2 = st.columns([2, 1])
            with c_det1:
                st.write(f"**Company Target:** {it['target_company'] or 'Tech Industry'}")
                st.write(f"**Grace Years:** {it['grace_years']} year(s)")
                st.write(f"**Interviewer:** {it['interviewer_persona']}")
                strengths = it.get("feedback", {}).get("top_strengths", [])
                if strengths:
                    st.caption("Key Strengths: " + "; ".join(strengths[:2]))
            with c_det2:
                report_file = Path(it.get("report_path", ""))
                if report_file.exists():
                    st.download_button(
                        label="📥 Download PDF",
                        data=get_pdf_bytes(str(report_file)),
                        file_name=report_file.name,
                        mime="application/pdf",
                        key=f"dash_pdf_{it['id']}"
                    )
