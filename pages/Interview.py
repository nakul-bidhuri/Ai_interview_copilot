import streamlit as st
import time
import uuid
from pathlib import Path
from datetime import datetime

from utils.resume_parser import extract_text_from_pdf, parse_resume
from ai.interviewer import generate_interview_plan, generate_walkie_reaction
from ai.evaluator import evaluate_interview
from database.database import save_interview
from utils.pdf_generator import generate_interview_pdf, get_pdf_bytes
from utils.audio_walkie_talkie import render_walkie_talkie_widget

st.set_page_config(
    page_title="Live Interview Studio | AI Interview Copilot Pro",
    page_icon="🎙️",
    layout="wide"
)

# Load CSS
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "interview_stage" not in st.session_state:
    st.session_state.interview_stage = "SETUP"  # SETUP, BRIEFING, LIVE, EVALUATION
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}
if "interview_plan" not in st.session_state:
    st.session_state.interview_plan = {}
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "eval_result" not in st.session_state:
    st.session_state.eval_result = {}
if "last_reaction" not in st.session_state:
    st.session_state.last_reaction = None
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None


# Helper to reset
def reset_interview():
    st.session_state.interview_stage = "SETUP"
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.resume_data = {}
    st.session_state.interview_plan = {}
    st.session_state.current_q_index = 0
    st.session_state.transcript = []
    st.session_state.eval_result = {}
    st.session_state.last_reaction = None
    st.session_state.pdf_path = None
    st.rerun()


# ==========================================
# STAGE 1: CANDIDATE & RESUME SETUP
# ==========================================
if st.session_state.interview_stage == "SETUP":
    st.markdown("<div class='main-title'>🎙️ AI Walkie-Talkie Interview Studio</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Upload your resume, select your target role, and let our AI interviewer prepare a custom mock session.</div>", unsafe_allow_html=True)

    col_setup, col_info = st.columns([1.6, 1], gap="large")

    with col_setup:
        st.markdown("### 📄 Step 1: Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF or TXT format)",
            type=["pdf", "txt"],
            help="AI will parse your projects, skills, and experience to generate tailored questions."
        )

        sample_resume_btn = st.checkbox("Or use sample software engineering student resume for quick practice", value=False)

        st.markdown("### 🎯 Step 2: Target Role & Interview Parameters")
        c1, c2 = st.columns(2)
        with c1:
            target_role = st.selectbox(
                "Target Job Role",
                [
                    "Software Engineer / Developer",
                    "Full Stack Web Developer",
                    "Frontend Engineer (React / Next.js)",
                    "Backend Engineer (Python / Node / Java)",
                    "Data Scientist / AI Engineer",
                    "Mobile App Developer (Flutter / Android)",
                    "DevOps / Cloud Engineer",
                    "Product Manager / Analyst"
                ]
            )
            experience_level = st.selectbox(
                "Experience Level",
                ["Fresher / Final Year Student", "Junior Developer (1-2 Years)", "Mid-Level Engineer (3-5 Years)", "Career Switcher / Transitioning"]
            )

        with c2:
            target_company = st.text_input("Target Company (Optional)", placeholder="e.g. Google, Amazon, Microsoft, Startup")
            grace_years = st.number_input(
                "Grace / Gap Years to Address (if any)",
                min_value=0,
                max_value=10,
                value=0,
                help="If you took a career gap or graduation delay, the AI will constructively teach you how to explain it with confidence!"
            )

        persona = st.selectbox(
            "Interviewer Persona & Style",
            [
                "Professional & Encouraging Tech Lead (Recommended)",
                "Friendly HR & Culture Specialist",
                "Strict FAANG Bar Raiser (Challenging)",
                "Startup Founder / CTO"
            ]
        )

        st.write("")
        if st.button("🚀 Analyze Resume & Prepare Interview", type="primary", use_container_width=True):
            raw_text = ""
            filename = "Sample_Resume.txt"

            if uploaded_file is not None:
                filename = uploaded_file.name
                if uploaded_file.type == "application/pdf":
                    raw_text = extract_text_from_pdf(uploaded_file.read())
                else:
                    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
            elif sample_resume_btn:
                raw_text = """
                NAKUL BIDHURI
                Computer Science Graduate | Email: nakul@example.com | Phone: +91 9876543210
                
                EDUCATION:
                B.Tech in Computer Science & Engineering (2020 - 2024), GPA: 8.5/10
                
                TECHNICAL SKILLS:
                Languages: Python, JavaScript, SQL, HTML/CSS
                Frameworks: Streamlit, FastAPI, React, Node.js, Django
                Databases & Tools: PostgreSQL, SQLite, Git, GitHub, Docker, Postman
                Concepts: REST APIs, Data Structures, Machine Learning, System Design Basics
                
                PROJECTS:
                1. AI Interview Copilot:
                   - Built an interactive conversational voice interview platform using Python, Streamlit, and LLMs.
                   - Implemented real-time Speech-to-Text and Text-to-Speech walkie-talkie mode for realistic practice.
                   - Integrated automated candidate evaluation, scoring, and PDF report generation.
                2. Real-Time Chat Application:
                   - Developed responsive multi-room web app using Node.js, WebSockets, and MongoDB.
                   - Handled concurrency for up to 500 simultaneous users with sub-50ms message latency.
                
                ACHIEVEMENTS & CERTIFICATIONS:
                - Solved 250+ problems on LeetCode across Data Structures and Algorithms.
                - Certified in Full Stack Python Development.
                """
            else:
                st.warning("Please upload a resume or check 'use sample software engineering student resume' to proceed.")
                st.stop()

            with st.spinner("🔍 Parsing resume and analyzing skills & projects..."):
                parsed = parse_resume(raw_text)
                # Store user configurations
                st.session_state.resume_data = parsed
                st.session_state.resume_filename = filename
                st.session_state.target_role = target_role
                st.session_state.target_company = target_company
                st.session_state.experience_level = experience_level
                st.session_state.grace_years = grace_years or parsed.get("detected_grace_years", 0)
                st.session_state.persona = persona

            with st.spinner("🤖 AI is crafting customized interview questions based on your background..."):
                plan = generate_interview_plan(
                    resume_data=parsed,
                    target_role=target_role,
                    target_company=target_company,
                    experience_level=experience_level,
                    grace_years=st.session_state.grace_years,
                    persona=persona,
                    api_key=st.session_state.get("api_key"),
                    provider=st.session_state.get("llm_provider", "gemini")
                )
                st.session_state.interview_plan = plan
                st.session_state.interview_stage = "BRIEFING"
                st.rerun()

    with col_info:
        st.markdown(
            """
            <div class="card" style="text-align: left;">
              <h3 style="color: #38bdf8;">✨ Why This Platform?</h3>
              <p style="color: #cbd5e1; font-size: 14px;">
                Most students get rejected not because of lack of knowledge, but due to 
                <b>nervousness, unprepared resume answers, and struggling to explain career gaps</b>.
              </p>
              <div style="margin-top: 15px;">
                <div class="pill-badge pill-blue">📄 Resume-Deep Parsing</div>
                <div class="pill-badge pill-green">📻 Walkie-Talkie Voice Mode</div>
                <div class="pill-badge pill-purple">⏳ Grace Years Coaching</div>
                <div class="pill-badge pill-amber">📊 Model Answers & PDF Report</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.markdown(
            """
            <div class="feature-box">
              <div class="feature-title">🎙️ Walkie-Talkie Voice Experience</div>
              <div class="feature-desc">
                Just like a real phone screening or technical interview round, the AI speaks its question out loud. 
                You press <b>Push-to-Talk</b> to speak your answer, and receive real-time audio interaction!
              </div>
            </div>

            <div class="feature-box">
              <div class="feature-title">💡 Grace Years & Gap Handling</div>
              <div class="feature-desc">
                Took time off or had gap years? Don't worry. The platform coaches you on positive framing, 
                confidence statements, and showcasing continuous learning.
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================
# STAGE 2: BRIEFING & ROADMAP
# ==========================================
elif st.session_state.interview_stage == "BRIEFING":
    st.markdown("<div class='main-title'>📋 Interview Briefing & Strategy</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Review your profile summary and interview plan before entering the live voice room.</div>", unsafe_allow_html=True)

    plan = st.session_state.interview_plan
    resume = st.session_state.resume_data

    col_prof, col_questions = st.columns([1, 1.5], gap="large")

    with col_prof:
        st.markdown("### 👤 Candidate Profile Detected")
        st.write(f"**Name:** {resume.get('candidate_name', 'Candidate')}")
        st.write(f"**Target Role:** {st.session_state.target_role}")
        st.write(f"**Target Company:** {st.session_state.target_company or 'Standard Tech Firm'}")
        st.write(f"**Identified Grace/Gap Years:** {st.session_state.grace_years} year(s)")

        st.markdown("#### 🛠️ Skills Identified:")
        skills = resume.get("skills", [])
        if skills:
            pills = " ".join([f"<span class='pill-badge pill-blue'>{s}</span>" for s in skills[:12]])
            st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
        else:
            st.info("Core software development and general computer science skills.")

        st.markdown("#### ⏳ Grace Years / Gap Advice:")
        st.info(plan.get("detected_grace_years_analysis", "Remember to frame any career gap positively around self-learning and project building."))

    with col_questions:
        st.markdown("### 🎯 Your Custom Interview Roadmap")
        questions = plan.get("questions", [])
        for q in questions:
            q_id = q.get("id", 1)
            q_type = q.get("type", "Interview Question")
            q_text = q.get("question", "")
            q_hint = q.get("hint_for_candidate", "")

            with st.expander(f"**Question {q_id}: {q_type}**", expanded=(q_id == 1)):
                st.markdown(f"**Question:** *\"{q_text}\"*")
                st.caption(f"💡 **Tip on how to answer:** {q_hint}")

        st.write("")
        c_back, c_start = st.columns(2)
        with c_back:
            if st.button("⬅ Adjust Setup", use_container_width=True):
                st.session_state.interview_stage = "SETUP"
                st.rerun()
        with c_start:
            if st.button("🎙️ Enter Walkie-Talkie Interview Room", type="primary", use_container_width=True):
                st.session_state.interview_stage = "LIVE"
                st.session_state.current_q_index = 0
                st.session_state.transcript = []
                st.session_state.last_reaction = None
                st.rerun()


# ==========================================
# STAGE 3: LIVE WALKIE-TALKIE INTERVIEW ROOM
# ==========================================
elif st.session_state.interview_stage == "LIVE":
    questions = st.session_state.interview_plan.get("questions", [])
    total_q = len(questions)
    curr_idx = st.session_state.current_q_index

    if curr_idx >= total_q:
        # Move to evaluation
        st.session_state.interview_stage = "EVALUATION"
        st.rerun()

    curr_question_obj = questions[curr_idx]
    q_id = curr_question_obj.get("id", curr_idx + 1)
    q_type = curr_question_obj.get("type", "Technical / Behavioral")
    q_text = curr_question_obj.get("question", "")
    q_focus = curr_question_obj.get("focus", "")
    q_hint = curr_question_obj.get("hint_for_candidate", "")

    # Top Bar: Progress and Persona
    prog_col1, prog_col2, prog_col3 = st.columns([2, 1, 1])
    with prog_col1:
        st.markdown(f"### 📻 Live Interview Room — Question {curr_idx + 1} of {total_q}")
        progress_val = (curr_idx) / total_q
        st.progress(progress_val)
    with prog_col2:
        st.markdown(f"**Interviewer:** `{st.session_state.persona.split('(')[0].strip()}`")
        st.caption(f"Role: {st.session_state.target_role}")
    with prog_col3:
        if st.button("🛑 Exit & Reset", help="Abort current interview"):
            reset_interview()

    # Previous question reaction banner if available
    if st.session_state.last_reaction:
        rx = st.session_state.last_reaction
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; padding: 12px 18px; border-radius: 10px; margin-bottom: 15px;">
              <span style="color: #34d399; font-weight: bold;">💬 Interviewer Reaction:</span>
              <p style="margin: 4px 0 0 0; color: #f1f5f9; font-size: 14px;">"{rx.get('greeting_reaction', '')} {rx.get('follow_up_note', '')}"</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Question Banner
    st.markdown(
        f"""
        <div class="question-banner">
          <div class="question-meta">{q_type} • FOCUS: {q_focus}</div>
          <div class="question-text">"{q_text}"</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Walkie-Talkie Component
    render_walkie_talkie_widget(
        current_question=q_text,
        candidate_name=st.session_state.resume_data.get("candidate_name", "Candidate"),
        interviewer_persona=st.session_state.persona,
        auto_speak=True
    )

    st.write("")

    # Candidate Spoken / Typed Answer Container
    st.markdown("#### 🎙️ Your Spoken Answer (Over the Walkie-Talkie)")
    with st.expander("💡 Pro Tip: How to put up your answer", expanded=False):
        st.info(q_hint)

    student_answer = st.text_area(
        "Spoken transcript appears here in real-time (you can also edit or type manually):",
        value="",
        height=140,
        placeholder="Click '🎙️ Tap to Speak' above and speak your answer. Your live words will appear here...",
        key=f"candidate_answer_{curr_idx}"
    )

    col_sub1, col_sub2 = st.columns([2, 1])

    with col_sub1:
        submit_btn = st.button("🚀 Transmit Answer (Over & Out)", type="primary", use_container_width=True)

    with col_sub2:
        skip_btn = st.button("⏩ Skip this question", use_container_width=True)

    if submit_btn or skip_btn:
        final_answer = student_answer.strip() if submit_btn else "Candidate skipped this question."

        with st.spinner("📻 AI Interviewer is listening, taking notes, and responding..."):
            reaction = generate_walkie_reaction(
                candidate_name=st.session_state.resume_data.get("candidate_name", "Candidate"),
                question=q_text,
                candidate_answer=final_answer,
                persona=st.session_state.persona,
                question_idx=curr_idx + 1,
                total_questions=total_q,
                api_key=st.session_state.get("api_key"),
                provider=st.session_state.get("llm_provider", "gemini")
            )

            # Store in transcript
            st.session_state.transcript.append({
                "id": q_id,
                "type": q_type,
                "question": q_text,
                "answer": final_answer,
                "reaction": reaction
            })

            st.session_state.last_reaction = reaction
            st.session_state.current_q_index += 1

            if st.session_state.current_q_index >= total_q:
                st.session_state.interview_stage = "EVALUATION"

            st.rerun()


# ==========================================
# STAGE 4: POST-INTERVIEW COMPREHENSIVE EVALUATION
# ==========================================
elif st.session_state.interview_stage == "EVALUATION":
    st.markdown("<div class='main-title'>🏆 Comprehensive Interview Performance Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Detailed scorecard, model answers, and coaching to help you ace your real interviews!</div>", unsafe_allow_html=True)

    # Run evaluation if not already done
    if not st.session_state.eval_result:
        with st.spinner("🧠 Executive AI Hiring Director is evaluating your complete interview transcript..."):
            eval_data = evaluate_interview(
                candidate_name=st.session_state.resume_data.get("candidate_name", "Candidate"),
                target_role=st.session_state.target_role,
                target_company=st.session_state.target_company,
                experience_level=st.session_state.experience_level,
                grace_years=st.session_state.grace_years,
                resume_summary=st.session_state.resume_data.get("projects_summary", ""),
                transcript=st.session_state.transcript,
                api_key=st.session_state.get("api_key"),
                provider=st.session_state.get("llm_provider", "gemini")
            )
            st.session_state.eval_result = eval_data

            # Generate PDF
            pdf_path = generate_interview_pdf(
                session_id=st.session_state.session_id,
                candidate_name=st.session_state.resume_data.get("candidate_name", "Candidate"),
                target_role=st.session_state.target_role,
                target_company=st.session_state.target_company,
                experience_level=st.session_state.experience_level,
                grace_years=st.session_state.grace_years,
                overall_score=eval_data.get("overall_score", 8.0),
                scores=eval_data.get("scores", {}),
                feedback=eval_data,
                transcript=st.session_state.transcript
            )
            st.session_state.pdf_path = pdf_path

            # Save in SQLite Database
            save_interview(
                session_id=st.session_state.session_id,
                candidate_name=st.session_state.resume_data.get("candidate_name", "Candidate"),
                target_role=st.session_state.target_role,
                target_company=st.session_state.target_company,
                experience_level=st.session_state.experience_level,
                grace_years=st.session_state.grace_years,
                interviewer_persona=st.session_state.persona,
                resume_filename=st.session_state.get("resume_filename", ""),
                resume_summary=st.session_state.resume_data.get("projects_summary", ""),
                overall_score=eval_data.get("overall_score", 8.0),
                scores=eval_data.get("scores", {}),
                transcript=st.session_state.transcript,
                feedback=eval_data,
                report_path=pdf_path
            )

    eval_data = st.session_state.eval_result
    overall = eval_data.get("overall_score", 8.0)
    verdict = eval_data.get("readiness_verdict", "Interview Ready")
    scores = eval_data.get("scores", {})

    # 1. Top Highlights
    top1, top2 = st.columns([1, 2], gap="large")

    with top1:
        st.markdown(
            f"""
            <div class="card">
              <h3>Overall Interview Score</h3>
              <div class="score-big">{overall:.1f} <span style="font-size: 22px; color: #94a3b8;">/ 10</span></div>
              <div style="margin-top: 10px;">
                <span class="pill-badge pill-green" style="font-size: 14px;">{verdict}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        # PDF Download Button
        if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
            pdf_bytes = get_pdf_bytes(st.session_state.pdf_path)
            st.download_button(
                label="📥 Download Official PDF Report",
                data=pdf_bytes,
                file_name=Path(st.session_state.pdf_path).name,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        if st.button("🔄 Practice Another Interview", use_container_width=True):
            reset_interview()

    with top2:
        st.markdown("### 📊 Competency Breakdown")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Technical Depth", f"{scores.get('technical_depth', 8.0):.1f} / 10")
            st.metric("Problem Solving", f"{scores.get('problem_solving', 8.0):.1f} / 10")
        with sc2:
            st.metric("Communication Clarity", f"{scores.get('communication_clarity', 8.0):.1f} / 10")
            st.metric("STAR Alignment", f"{scores.get('star_method_alignment', 7.5):.1f} / 10")
        with sc3:
            st.metric("Confidence & Delivery", f"{scores.get('confidence_delivery', 8.0):.1f} / 10")
            st.metric("Grace Years Handling", "Strong" if st.session_state.grace_years > 0 else "N/A")

    st.write("")
    st.divider()

    # 2. Strengths & Improvements
    c_str, c_imp = st.columns(2, gap="medium")

    with c_str:
        st.markdown("### 💪 Your Top Strengths")
        for s in eval_data.get("top_strengths", []):
            st.success(f"✔ **{s}**")

    with c_imp:
        st.markdown("### 🎯 Critical Areas to Improve Before Real Interview")
        for imp in eval_data.get("critical_areas_for_improvement", []):
            st.warning(f"⚡ **{imp}**")

    # 3. Grace & Gap Years Masterclass
    st.write("")
    st.markdown("### ⏳ Grace Years & Gap Handling Masterclass")
    gy = eval_data.get("grace_years_coaching", {})
    if isinstance(gy, dict):
        st.markdown(f"**Interviewer Coaching Analysis:** {gy.get('analysis', '')}")
        st.markdown(
            f"""
            <div style="background: rgba(0, 114, 255, 0.12); border-left: 4px solid #0072ff; padding: 15px 20px; border-radius: 10px; margin: 12px 0;">
              <span style="color: #38bdf8; font-weight: bold; font-size: 13px;">🎯 YOUR EXACT POWER STATEMENT TO SAY IN INTERVIEWS:</span>
              <p style="margin: 6px 0 0 0; color: #ffffff; font-size: 15px; font-style: italic;">
                "{gy.get('power_statement', 'During my gap period, I focused on disciplined upskilling and building production-grade projects.')}"
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Question-by-Question Review with Model Answers
    st.write("")
    st.markdown("### 📝 Question-by-Question Critique & Model Answers")
    st.caption("Compare what you said with how an elite engineer would answer the question.")

    reviews = eval_data.get("questions_review", [])
    for idx, rev in enumerate(reviews, 1):
        with st.expander(f"**Q{idx}: {rev.get('question', f'Question {idx}')}** (Score: {rev.get('score', 8.0)}/10)", expanded=(idx == 1)):
            st.markdown(f"**Interviewer Critique:** {rev.get('feedback', '')}")
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-top: 8px;">
                  <span style="color: #38bdf8; font-weight: 600;">💎 Model Answer (How to Answer Like a Pro):</span>
                  <p style="margin: 6px 0 0 0; color: #e2e8f0; font-size: 14px;">"{rev.get('model_answer', '')}"</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 5. Interviewer Etiquette Masterclass
    st.write("")
    st.markdown("### 🎓 How to Deal with Tough Interviewers (Tactical Guide)")
    tips = eval_data.get("interviewer_masterclass_tips", [
        "If you don't know the exact answer, explain your reasoning process: 'I haven't encountered that specific edge case yet, but here is how I would troubleshoot it logically...'",
        "Use the STAR technique (Situation, Task, Action, Result) for all scenario questions.",
        "Always prepare 2 thoughtful questions to ask the interviewer at the end of the round."
    ])
    for t in tips:
        st.info(f"💡 {t}")
