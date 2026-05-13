import streamlit as st

from ui.layout import render_section_header


def render_problem_section() -> None:
    render_section_header(
        "01",
        "The Problem",
        "Static defenses fail against evolving attacks",
        "A research-grade defense must adapt as threats mutate. We treat security as a living system, not a checklist.",
        "problem",
    )
    st.markdown(
        """
<div class="problem-panel">
  <div>
    <p><b style="color:#eef7ff;">Most LLM defenses today rely on keyword filters, hardcoded rules,
    fixed classifiers, and one-time safety prompts.</b> They are static snapshots of yesterday's threats.</p>
    <p>Attackers do not stand still. They mutate phrasing, chain steps, swap roles, and probe memory.
    Each new variant slips past brittle rules. The defense must <span class="accent">evolve</span>, or it decays.</p>
  </div>
  <div class="chip-grid">
    <div class="chip red">keyword filters</div>
    <div class="chip red">hardcoded rules</div>
    <div class="chip orange">fixed classifiers</div>
    <div class="chip orange">one-time prompts</div>
    <div class="chip cyan">adaptive loop</div>
    <div class="chip green">continual learning</div>
  </div>
</div>
<div class="threat-grid">
  <div class="threat-card">
    <div class="threat-head"><div class="threat-title">Prompt Injection</div><div class="threat-level">HIGH</div></div>
    <p class="threat-desc">Adversarial text crafted to hijack instructions or smuggle hidden directives into model reasoning.</p>
    <div class="codebox">// example - [redacted prompt injection pattern] - safe-mode preview</div>
  </div>
  <div class="threat-card">
    <div class="threat-head"><div class="threat-title">Jailbreak Attempt</div><div class="threat-level">HIGH</div></div>
    <p class="threat-desc">Layered persona, role-play, and multi-step framing intended to dissolve safety alignment.</p>
    <div class="codebox">// example - instruction hierarchy override pattern - safe-mode preview</div>
  </div>
  <div class="threat-card">
    <div class="threat-head"><div class="threat-title">Data Exfiltration Attempt</div><div class="threat-level">CRITICAL</div></div>
    <p class="threat-desc">Probes that try to extract system prompts, hidden context, embedded secrets, or memory contents.</p>
    <div class="codebox">// example - simulated data-exfiltration probe - safe-mode preview</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
