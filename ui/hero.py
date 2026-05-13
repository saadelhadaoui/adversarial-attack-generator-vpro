import streamlit as st


def render_hero() -> None:
    st.markdown(
        """
<div class="glass">
  <h1>Adaptive Multi-Agent LLM Defense Lab</h1>
  <p>
    A safe, synthetic AI security lab where a Defender, Evaluator, and Learning
    Agent adapt from adversarial test patterns and persist lessons in SQLite.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
