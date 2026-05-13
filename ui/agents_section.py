import streamlit as st

from ui.layout import render_section_header


def render_agents_section() -> None:
    render_section_header("02", "Agents", "Four cooperating agents", "Each agent owns a specific part of the defense loop.", "agents")
    cols = st.columns(4)
    for col, title, desc in zip(
        cols,
        ["Attacker", "Defender", "Evaluator", "Learner"],
        [
            "Generates safe redacted probes.",
            "Scores risk and chooses PASS, BLOCK, REFORMULATE, or monitoring.",
            "Checks whether synthetic internal data leaked.",
            "Stores learned patterns and rules in SQLite.",
        ],
    ):
        col.markdown(f'<div class="glass"><b>{title}</b><br>{desc}</div>', unsafe_allow_html=True)
