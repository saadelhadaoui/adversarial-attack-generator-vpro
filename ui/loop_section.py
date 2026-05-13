import streamlit as st

from ui.layout import render_section_header


def render_loop_section() -> None:
    render_section_header("03", "Loop", "Closed feedback loop", "Every interaction is evaluated and may update memory.", "loop")
    st.markdown(
        '<div class="glass">Input -> Defender -> Assistant -> Evaluator -> Learner -> SQLite -> Updated Defender</div>',
        unsafe_allow_html=True,
    )
