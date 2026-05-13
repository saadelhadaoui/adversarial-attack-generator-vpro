import streamlit as st

from ui.layout import render_section_header
from visualizations.diagrams import render_architecture_diagram_html


def render_architecture_section() -> None:
    render_section_header("08", "Architecture", "Backend architecture", "The UI calls one adapter, which calls the real DefenseGraph.", "architecture")
    st.markdown(render_architecture_diagram_html(), unsafe_allow_html=True)
