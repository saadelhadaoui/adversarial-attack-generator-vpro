import streamlit as st


def render_top_nav() -> None:
    st.markdown(
        """
<div class="topnav">
  <div class="brand"><span class="dot"></span>Adaptive Multi-Agent LLM Defense Lab</div>
  <div class="links">
    <a href="#arena">Arena</a>
    <a href="#simulation">Simulation</a>
    <a href="#memory">Memory</a>
    <a href="#evaluation">Evaluation</a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_header(num: str, eyebrow: str, title: str, subtitle: str, anchor: str) -> None:
    st.markdown(
        f"""
<div id="{anchor}" class="section">
  <div class="section-header">
    <span class="num">{num}</span>
    <span class="eyebrow">{eyebrow}</span>
  </div>
  <div class="section-title">{title}</div>
  <div class="section-sub">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown('<div class="footer">Safe synthetic data only. Built for defensive research demos.</div>', unsafe_allow_html=True)
