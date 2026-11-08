import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Data Profile & Blog | AI Interview Copilot Pro",
    page_icon="📖",
    layout="wide"
)

# Load CSS
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

blog_path = Path("BLOG.md")
if blog_path.exists():
    with open(blog_path, "r", encoding="utf-8") as f:
        blog_content = f.read()
    st.markdown(blog_content, unsafe_allow_html=True)
else:
    st.info("Blog file not found.")

st.write("")
st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Practice Mock Interview Now", type="primary", use_container_width=True):
        st.switch_page("pages/Interview.py")
with col2:
    if st.button("📊 View Performance Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
