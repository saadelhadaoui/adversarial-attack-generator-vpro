import streamlit as st

from ui.layout import render_section_header


def render_problem_section() -> None:
    render_section_header(
        "01",
        "Problem",
        "Static defenses fall behind",
        "The demo shows how learned patterns and rules can update the Defender after observed failures.",
        "problem",
    )
    st.markdown(
        '<div class="glass">All attacks are redacted or synthetic. The goal is defensive evaluation, not payload generation.</div>',
        unsafe_allow_html=True,
    )
