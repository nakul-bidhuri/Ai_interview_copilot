import streamlit as st
from pathlib import Path
from database.database import get_dashboard_metrics, init_db

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="AI Interview Copilot Pro | Resume-Driven Voice Mock Interviews",
    page_icon="🎯",
    layout="wide"
)

# Load CSS
def load_css():
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Hero Section
st.markdown(
    """
    <div class="main-title">🎯 AI Interview Copilot Pro</div>
    <div class="subtitle">
      The Next-Gen Resume-Driven Mock Interview Platform for Students & Engineers.<br>
      Experience realistic <b>Walkie-Talkie voice rounds</b>, master tough technical questions, and conquer grace/gap years.
    </div>
    """,
    unsafe_allow_html=True
)

# Dynamic Dashboard Cards from SQLite
metrics = get_dashboard_metrics()
tot_interviews = metrics.get("total_interviews", 0)
avg_score = metrics.get("average_score", 0.0)
best_score = metrics.get("best_score", 0.0)
tot_reports = metrics.get("total_reports", 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card">
          <h3>Total Mock Interviews</h3>
          <h1>{tot_interviews if tot_interviews > 0 else '0'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
          <h3>Average Score</h3>
          <h1>{f'{avg_score:.1f}' if tot_interviews > 0 else '—'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
          <h3>Top Candidate Score</h3>
          <h1>{f'{best_score:.1f}' if tot_interviews > 0 else '—'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="card">
          <h3>PDF Reports Generated</h3>
          <h1>{tot_reports if tot_reports > 0 else '0'}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.write("")

# Call to Action Center
cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    if st.button("🚀 Start Live Interview Studio Now", type="primary", use_container_width=True):
        st.switch_page("pages/Interview.py")

st.write("")
st.divider()

# Core Platform Capabilities Showcase
st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 25px;'>Why Practice with AI Interview Copilot?</h2>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3, gap="medium")

with f1:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">📄</div>
          <div class="feature-title">Resume-Deep Question Generation</div>
          <div class="feature-desc">
            No generic questions. The AI thoroughly scans your uploaded resume, your exact projects, 
            tech stack choices, and architecture decisions to ask probing technical questions just like real tech leads.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f2:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">📻</div>
          <div class="feature-title">Walkie-Talkie Conversational Voice Mode</div>
          <div class="feature-desc">
            Simulate real remote phone screenings. The AI interviewer speaks the question out loud (TTS), 
            and you push-to-talk to respond using live speech recognition (STT) with audio chirps!
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">⏳</div>
          <div class="feature-title">Grace Years & Career Gap Coaching</div>
          <div class="feature-desc">
            Struggling to explain graduation delays or career gap years? The platform analyzes your timeline 
            and arms you with positive, high-confidence "Power Statements" that impress recruiters.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

f4, f5, f6 = st.columns(3, gap="medium")

with f4:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">💎</div>
          <div class="feature-title">Pro Model Answers for Every Question</div>
          <div class="feature-desc">
            Don't just see a score—learn how an elite senior engineer would structure the answer. 
            Includes STAR method guidelines, technical depth, and communication framing.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f5:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">📊</div>
          <div class="feature-title">Comprehensive PDF Evaluation Reports</div>
          <div class="feature-desc">
            Download a beautifully formatted, multi-page PDF performance report complete with score breakdowns, 
            competency charts, interviewer critiques, and actionable preparation checklists.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f6:
    st.markdown(
        """
        <div class="feature-box">
          <div class="feature-icon">⚡</div>
          <div class="feature-title">Multi-Model & Zero-Cost Simulation</div>
          <div class="feature-desc">
            Connect Google Gemini, OpenAI, or Groq—or use our built-in intelligent offline simulator 
            for immediate, zero-credential practice right out of the box.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.divider()

# Quick Navigation Footer
st.markdown("### 🧭 Quick Navigation")
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("📊 View Performance Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
with nav2:
    if st.button("📜 Browse Past Transcripts & History", use_container_width=True):
        st.switch_page("pages/History.py")
with nav3:
    if st.button("⚙️ Open Settings & AI Keys", use_container_width=True):
        st.switch_page("pages/Settings.py")
