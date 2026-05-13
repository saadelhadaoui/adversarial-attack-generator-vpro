import os

import streamlit as st

from ui.layout import render_section_header


def _package_card(path: str, files: str) -> str:
    present = os.path.isdir(path)
    label = "present" if present else "missing"
    return f"""
<div class="arch-card">
  <span class="present">{label}</span>
  <h4>{path}/</h4>
  <p>{files}</p>
</div>
"""


def render_architecture_section() -> None:
    render_section_header(
        "08",
        "Architecture",
        "Auditable state and backend packages",
        "The UI calls one adapter, which calls the real DefenseGraph and writes state to SQLite.",
        "architecture",
    )
    st.markdown(
        """
<div class="glass arch-state">
  <span class="eyebrow">Shared State</span>
  <div class="arch-state-grid">
    <div><b>current_attack</b></div>
    <div><b>attack_family</b></div>
    <div><b>attack_strategy</b></div>
    <div><b>defender_response</b></div>
    <div><b>evaluator_scores</b></div>
    <div><b>learner_updates</b></div>
    <div><b>iteration_count</b></div>
    <div><b>history</b></div>
    <div><b>convergence_status</b></div>
  </div>
</div>
<div class="feed">persisted to memory layer</div>
<div class="arch-memory-grid">
  <div class="memory-card"><h4>Vector Memory (FAISS-like)</h4><p>semantic similarity over abstract patterns</p></div>
  <div class="memory-card purple"><h4>Structured Memory (SQLite-like)</h4><p>iteration logs - rules - scores</p></div>
</div>
<div class="glass arch-state" style="border-color:rgba(34,197,94,.28);">
  <span class="eyebrow" style="color:#b5f7c9;border-color:rgba(34,197,94,.45);">Stop Conditions</span>
  <div class="arch-state-grid">
    <div><b>max_iterations_reached</b></div>
    <div><b>defense_score &gt; 0.95 x 10</b></div>
    <div><b>manual_stop</b></div>
  </div>
</div>
<span class="eyebrow" style="margin-top:1rem;">Backend Packages - Detected</span>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="arch-packages">'
        + _package_card("attacker_agent", "safe_templates.py, strategies.py, agent.py")
        + _package_card("defender_agent", "policy.py, risk_rules.py, agent.py")
        + _package_card("evaluator_agent", "scoring.py, agent.py")
        + _package_card("learning_agent", "pattern_extractor.py, rule_generator.py")
        + _package_card("orchestration", "state.py, graph.py")
        + "</div>",
        unsafe_allow_html=True,
    )
