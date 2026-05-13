import streamlit as st

from utils.project_loader import load_available_datasets, load_seed_data_if_available


def render_hero() -> None:
    dataset_count = len(load_available_datasets())
    seed_state = "ready" if load_seed_data_if_available().get("seed_script") else "missing"
    st.markdown(
        f"""
<div class="hero-card">
  <div class="hero-kicker"><span class="eyebrow">Cybersecurity - AI - Adaptive Defense</span></div>
  <h1 class="hero-title">Adaptive Multi-Agent<br>LLM Defense <span>Lab</span></h1>
  <div class="hero-subtitle">A living AI security system that learns from every attack.</div>
  <p class="hero-copy">
    Instead of relying on static filters, this system uses four cooperating agents to
    <b>attack</b>, <b>defend</b>, <b>evaluate</b>, and <b>learn</b>
    continuously, turning every adversarial probe into a lesson that strengthens the defender.
  </p>
  <div class="hero-actions">
    <a class="hero-btn" href="#arena">Explore the System</a>
    <a class="hero-btn secondary" href="#simulation">Run Safe Simulation</a>
    <a class="hero-btn secondary" href="#architecture">View Architecture</a>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><div class="label">Agents Online</div><div class="value">5/5</div></div>
    <div class="hero-stat"><div class="label">Datasets Detected</div><div class="value">{dataset_count}</div></div>
    <div class="hero-stat"><div class="label">Seed Script</div><div class="value" style="color:#22ff88;">{seed_state}</div></div>
    <div class="hero-stat"><div class="label">Mode</div><div class="value">SAFE-DEMO</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
