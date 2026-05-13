import streamlit as st

from ui.layout import render_section_header


def render_loop_section() -> None:
    render_section_header(
        "03",
        "Adaptive Loop",
        "A closed feedback loop, not a static filter",
        "The system watches outcomes, stores memory, and changes the next decision.",
        "loop",
    )
    st.markdown(
        """
<div class="loop-wrap">
  <div class="glass orbit-card">
    <div class="orbit"></div>
    <div class="orbit-node" style="left:50%;top:13%;">Attacker</div>
    <div class="orbit-node" style="left:85%;top:48%;">Defender</div>
    <div class="orbit-node" style="left:62%;top:86%;">Evaluator</div>
    <div class="orbit-node" style="left:25%;top:72%;">Learner</div>
    <div class="orbit-node" style="left:19%;top:30%;border-color:rgba(249,115,22,.45);color:#fdba74;">Memory</div>
  </div>
  <div class="glass timeline">
    <span class="eyebrow">Safe Scenario Timeline</span>
    <div class="timeline-row"><small>ROUND 01</small><br>A simulated context-manipulation pattern partially bypasses the Defender.</div>
    <div class="timeline-row"><small>ROUND 05</small><br>A close variant appears. The Defender recognizes the abstract structure and reformulates safely.</div>
    <div class="timeline-row"><small>ROUND 20</small><br>Attacker shifts to multi-step ambiguity. The system continues to learn.</div>
    <div class="timeline-row"><small>ROUND 40+</small><br>Defense score holds above 0.95 across families.</div>
  </div>
</div>
<div class="loop-steps">
  <div class="glass loop-step"><b>Attacker</b><span>generates safe probe</span></div>
  <div class="glass loop-step"><b>Defender</b><span>BLOCK - REFORMULATE - PASS</span></div>
  <div class="glass loop-step"><b>Evaluator</b><span>judges defense quality</span></div>
  <div class="glass loop-step"><b>Learning Agent</b><span>extracts new patterns</span></div>
  <div class="glass loop-step"><b>Memory Update</b><span>structured store</span></div>
</div>
<div class="feed">feeds back into the next iteration</div>
""",
        unsafe_allow_html=True,
    )
