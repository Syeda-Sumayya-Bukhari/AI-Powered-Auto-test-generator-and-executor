"""
Optional web UI (requires Streamlit — Python 3.10–3.12 recommended).

  pip install streamlit
  streamlit run ui_web.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    import streamlit as st
except ImportError as exc:
    raise SystemExit(
        "Streamlit not installed or not supported on your Python version.\n"
        "Use the desktop UI instead:  python ui_app.py"
    ) from exc

from src.config import BASE_URL
from src.pipeline import MODULE_PRESETS, build_requirement, execute_plan, generate_plan

st.set_page_config(page_title="AI Test Automation", page_icon="🧪", layout="wide")

if "test_plan" not in st.session_state:
    st.session_state.test_plan = None
if "summary" not in st.session_state:
    st.session_state.summary = None

st.title("AI Test Case Generator + Auto Execution")
st.caption(f"Sauce Demo — {BASE_URL}")

with st.sidebar:
    ai_provider = st.selectbox("AI provider", ["mock", "gemini", "groq", "ollama", "openai"])
    headless = st.checkbox("Headless browser", value=True)

module = st.selectbox("Module", list(MODULE_PRESETS.keys()))
default = "" if module == "Custom" else MODULE_PRESETS.get(module, "")
requirement_input = st.text_area("Requirement", value=default, height=100)
full_requirement = build_requirement(module, requirement_input)

c1, c2, c3 = st.columns(3)
gen = c1.button("Generate test cases")
exe = c2.button("Execute tests")
both = c3.button("Generate & Execute", type="primary")

if gen or both:
    with st.spinner("Generating..."):
        st.session_state.test_plan = generate_plan(full_requirement, ai_provider=ai_provider)
        st.success("Test cases generated.")

if (exe or both) and st.session_state.test_plan:
    with st.spinner("Running Selenium..."):
        _, payload, jp, hp = execute_plan(st.session_state.test_plan, headless=headless)
        st.session_state.summary = payload
        st.metric("Pass rate", f"{payload['summary']['pass_rate']}%")
        st.json(payload)
        st.code(str(hp))

if st.session_state.test_plan:
    with st.expander("Test plan"):
        st.json(st.session_state.test_plan)
