import streamlit as st

from ui.layout import render_section_header


def render_agents_section() -> None:
    render_section_header(
        "02",
        "The Agents",
        "Four agents. One adaptive immune system.",
        "Each agent has a distinct role. Together they form a closed feedback loop where every attack feeds learning.",
        "agents",
    )
    st.markdown(
        """
<div class="agent-grid">
  <div class="agent-card red">
    <div class="role">Red team - simulated only</div>
    <h3>Attacker Agent</h3>
    <p>Generates safe simulated adversarial probes and searches for Defender weaknesses. No real harmful payloads are produced or stored.</p>
    <ul><li>choose attack family</li><li>mutate safe redacted patterns</li><li>probe learned defenses</li></ul>
  </div>
  <div class="agent-card cyan">
    <div class="role">Blue team - primary shield</div>
    <h3>Defender Agent</h3>
    <p>Analyzes every input and decides BLOCK, REFORMULATE, PASS, or controlled monitoring using rules and memory.</p>
    <ul><li>detect known abstract patterns</li><li>calculate risk score</li><li>apply mode-aware policy</li></ul>
  </div>
  <div class="agent-card purple">
    <div class="role">Independent judge</div>
    <h3>Evaluator Agent</h3>
    <p>Audits the interaction, detects synthetic honeytokens, flags false positives, and assigns a defense score.</p>
    <ul><li>detect data leaks</li><li>score defense quality</li><li>separate blocks from false positives</li></ul>
  </div>
  <div class="agent-card green">
    <div class="role">Continual learner</div>
    <h3>Learning Agent</h3>
    <p>Extracts reusable abstract patterns from failures and risky monitored events, then writes new rules to SQLite.</p>
    <ul><li>extract pattern label</li><li>generate symbolic rule</li><li>update persistent memory</li></ul>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
