import pandas as pd
import plotly.express as px
import streamlit as st

from ui.layout import render_section_header
from utils.chatbot_engine import get_defender_rules, get_learned_patterns, get_metrics, get_rag_events, get_recent_interactions
from visualizations.charts import PLOT_LAYOUT
from visualizations.diagrams import render_memory_diagram_html


def render_memory_section() -> None:
    render_section_header("08", "Memory", "Live SQLite memory", "These tables are read directly from data/defense_lab.db.", "memory")
    st.markdown(render_memory_diagram_html(), unsafe_allow_html=True)

    st.markdown(
        """
<div class="memory-split">
  <div class="memory-card">
    <span class="pill">Vector Memory</span>
    <h4>FAISS-like semantic store</h4>
    <p><i>"Does this new probe resemble something we've seen?"</i></p>
    <div class="memory-list">
      <div class="memory-item">context manipulation pattern</div>
      <div class="memory-item">role confusion pattern</div>
      <div class="memory-item">multi-step ambiguity pattern</div>
      <div class="memory-item">memory probing pattern</div>
    </div>
  </div>
  <div class="memory-card purple">
    <span class="pill purple">Structured Memory</span>
    <h4>SQLite-like log store</h4>
    <p><i>"What exactly happened at iteration X?"</i></p>
    <div class="memory-list">
      <div class="memory-item">iteration logs - per-family scores</div>
      <div class="memory-item">extracted rules and defender updates</div>
      <div class="memory-item">convergence history</div>
      <div class="memory-item">false positive history</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Refresh Memory", key="memory_refresh"):
        st.rerun()

    metrics = get_metrics()
    cols = st.columns(5)
    cols[0].metric("Interactions", metrics.get("total_interactions", 0))
    cols[1].metric("Patterns", metrics.get("learned_patterns_count", 0))
    cols[2].metric("Rules", metrics.get("defender_rules_count", 0))
    cols[3].metric("Honeytokens", metrics.get("honeytoken_detections", 0))
    cols[4].metric("Avg Defense", f"{metrics.get('avg_defense_score', 0):.3f}")

    tab_patterns, tab_rules, tab_rag, tab_interactions = st.tabs(["Patterns", "Rules", "RAG Events", "Interactions"])
    patterns = pd.DataFrame(get_learned_patterns())
    with tab_patterns:
        if patterns.empty:
            st.info("No learned patterns yet. Run a controlled exfiltration attempt in the Chatbot Arena.")
        else:
            st.dataframe(patterns, use_container_width=True)
        if not patterns.empty and "threat_family" in patterns:
            counts = patterns["threat_family"].value_counts().reset_index()
            counts.columns = ["threat_family", "count"]
            fig = px.bar(counts, x="threat_family", y="count", color="threat_family", title="Patterns by family")
            fig.update_layout(**PLOT_LAYOUT, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    with tab_rules:
        st.dataframe(pd.DataFrame(get_defender_rules()), use_container_width=True)
    with tab_rag:
        st.dataframe(pd.DataFrame(get_rag_events(100)), use_container_width=True)
    with tab_interactions:
        st.dataframe(pd.DataFrame(get_recent_interactions(100)), use_container_width=True)
