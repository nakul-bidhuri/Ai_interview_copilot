import streamlit as st
import os
from pathlib import Path
from dotenv import set_key

st.set_page_config(
    page_title="Settings & AI Configuration | AI Interview Copilot Pro",
    page_icon="⚙️",
    layout="wide"
)

# Load CSS
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='main-title'>⚙️ Platform Settings & AI Model Configuration</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Configure your AI provider keys, customize audio walkie-talkie preferences, and manage platform data.</div>", unsafe_allow_html=True)

col_settings, col_info = st.columns([1.6, 1], gap="large")

with col_settings:
    st.markdown("### 🤖 1. LLM Provider Configuration")
    
    provider = st.selectbox(
        "Active LLM Engine",
        ["Google Gemini (Recommended)", "OpenAI / ChatGPT", "Groq (Ultra-Fast)", "Built-in Offline Simulator (Free / No Keys Required)"],
        index=0
    )

    env_path = Path(".env")

    if provider == "Google Gemini (Recommended)":
        st.session_state.llm_provider = "gemini"
        default_gemini = os.getenv("GEMINI_API_KEY", "")
        gemini_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.get("gemini_key", default_gemini),
            type="password",
            help="Get your free key from https://aistudio.google.com/app/apikey"
        )
        if gemini_key:
            st.session_state.api_key = gemini_key
            st.session_state.gemini_key = gemini_key

    elif provider == "OpenAI / ChatGPT":
        st.session_state.llm_provider = "openai"
        default_openai = os.getenv("OPENAI_API_KEY", "")
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get("openai_key", default_openai),
            type="password",
            help="Get your key from https://platform.openai.com/api-keys"
        )
        if openai_key:
            st.session_state.api_key = openai_key
            st.session_state.openai_key = openai_key

    elif provider == "Groq (Ultra-Fast)":
        st.session_state.llm_provider = "groq"
        default_groq = os.getenv("GROQ_API_KEY", "")
        groq_key = st.text_input(
            "Groq API Key",
            value=st.session_state.get("groq_key", default_groq),
            type="password",
            help="Get your free fast key from https://console.groq.com/keys"
        )
        if groq_key:
            st.session_state.api_key = groq_key
            st.session_state.groq_key = groq_key

    else:
        st.session_state.llm_provider = "simulator"
        st.session_state.api_key = None
        st.success("🟢 Built-in Offline Simulation Engine active. Fully functional without needing an external API key!")

    # Save to .env button
    c_save, c_test = st.columns(2)
    with c_save:
        if st.button("💾 Save Key to .env File", use_container_width=True):
            if not env_path.exists():
                env_path.touch()
            key_val = st.session_state.get("api_key", "")
            if st.session_state.get("llm_provider") == "gemini" and key_val:
                set_key(str(env_path), "GEMINI_API_KEY", key_val)
                os.environ["GEMINI_API_KEY"] = key_val
                st.success("Gemini API key saved to .env!")
            elif st.session_state.get("llm_provider") == "openai" and key_val:
                set_key(str(env_path), "OPENAI_API_KEY", key_val)
                os.environ["OPENAI_API_KEY"] = key_val
                st.success("OpenAI API key saved to .env!")
            elif st.session_state.get("llm_provider") == "groq" and key_val:
                set_key(str(env_path), "GROQ_API_KEY", key_val)
                os.environ["GROQ_API_KEY"] = key_val
                st.success("Groq API key saved to .env!")
            else:
                st.info("No active external key to save. Running on offline simulator.")

    with c_test:
        if st.button("⚡ Test AI Connection", use_container_width=True):
            from ai.llm import call_llm
            with st.spinner("Testing AI handshake..."):
                resp = call_llm(
                    prompt="Hello! Say one sentence welcoming a student to their mock interview.",
                    api_key=st.session_state.get("api_key"),
                    provider=st.session_state.get("llm_provider", "gemini")
                )
                st.success(f"Response: {resp}")

    st.write("")
    st.divider()

    st.markdown("### 🎙️ 2. Audio & Walkie-Talkie Settings")
    st.selectbox("Default Interviewer Voice Accent", ["US English (Natural)", "UK English (Received Pronunciation)", "Indian English"])
    st.slider("Voice Speech Rate", min_value=0.75, max_value=1.5, value=1.0, step=0.05)
    st.checkbox("Auto-speak questions immediately upon entering room", value=True)

with col_info:
    st.markdown(
        """
        <div class="card" style="text-align: left;">
          <h3 style="color: #38bdf8;">🔒 Privacy & Security</h3>
          <p style="color: #cbd5e1; font-size: 13.5px; line-height: 1.5;">
            Your API keys are stored locally on your machine (in memory or optional local <code>.env</code> file). 
            They are never transmitted to any third-party analytics servers.
          </p>
          <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 15px 0;">
          <h3 style="color: #34d399;">💡 Offline Mode</h3>
          <p style="color: #cbd5e1; font-size: 13.5px; line-height: 1.5;">
            Even if you have no internet access or API credits, the platform's 
            <b>Intelligent Offline Simulator</b> will dynamically generate realistic, 
            high-fidelity technical questions, walkie-talkie audio transcripts, and reports.
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )
