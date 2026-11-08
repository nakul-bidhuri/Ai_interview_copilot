import streamlit as st
from pathlib import Path
from database.database import get_all_interviews, delete_interview
from utils.pdf_generator import get_pdf_bytes

st.set_page_config(
    page_title="Interview Archive & Transcripts | AI Interview Copilot Pro",
    page_icon="📜",
    layout="wide"
)

# Load CSS
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='main-title'>📜 Interview Session Archive</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Review full Q&A transcripts, feedback breakdowns, and past candidate evaluation reports.</div>", unsafe_allow_html=True)

interviews = get_all_interviews()

if not interviews:
    st.info("No saved interview sessions found in the database. Complete a live interview to see your archive here.")
    if st.button("🚀 Start New Interview", type="primary"):
        st.switch_page("pages/Interview.py")
else:
    # Filter / Search bar
    search_query = st.text_input("🔍 Search past sessions by candidate name or target role:", "")

    filtered = [
        it for it in interviews
        if search_query.lower() in it["candidate_name"].lower() or search_query.lower() in it["target_role"].lower()
    ]

    st.write(f"Showing **{len(filtered)}** interview session(s):")

    for it in filtered:
        session_id = it["id"]
        created = it["created_at"]
        name = it["candidate_name"]
        role = it["target_role"]
        company = it["target_company"] or "Industry Standard"
        score = it["overall_score"]
        report_path = Path(it.get("report_path", ""))

        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <span style="font-size: 18px; font-weight: bold; color: #f8fafc;">{role}</span>
                      <span style="color: #94a3b8; font-size: 14px;"> — {company}</span>
                      <div style="color: #64748b; font-size: 12px; margin-top: 2px;">Candidate: <b>{name}</b> | Date: {created} | Grace Years: {it['grace_years']} yr</div>
                    </div>
                    <div style="text-align: right;">
                      <span style="font-size: 24px; font-weight: 800; color: #38bdf8;">{score:.1f}</span>
                      <span style="font-size: 14px; color: #94a3b8;">/ 10</span>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"View Full Q&A Transcript & Feedback for {name}"):
                c1, c2 = st.columns([3, 1])

                with c1:
                    st.markdown("#### 💬 Conversation Transcript:")
                    transcript = it.get("transcript", [])
                    if transcript:
                        for q_idx, item in enumerate(transcript, 1):
                            q_text = item.get("question", "")
                            ans_text = item.get("answer", "")
                            st.markdown(f"**Q{q_idx}:** *{q_text}*")
                            st.markdown(f"**Your Answer:** *\"{ans_text}\"*")
                            st.divider()
                    else:
                        st.write("No transcript recorded.")

                with c2:
                    st.markdown("#### 📊 Actions & Report:")
                    if report_path.exists():
                        st.download_button(
                            label="📥 Download PDF",
                            data=get_pdf_bytes(str(report_path)),
                            file_name=report_path.name,
                            mime="application/pdf",
                            key=f"hist_pdf_{session_id}",
                            use_container_width=True
                        )

                    st.write("")
                    if st.button("🗑️ Delete Session", key=f"del_{session_id}", use_container_width=True):
                        delete_interview(session_id)
                        st.success("Session deleted successfully!")
                        st.rerun()
