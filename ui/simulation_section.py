import pandas as pd
import streamlit as st

from ui.components import console_block, console_line
from ui.layout import render_section_header
from utils.chatbot_engine import get_metrics, get_recent_interactions
from visualizations.charts import action_distribution_chart


def render_simulation_section() -> None:
    render_section_header("06", "Simulation", "Real pipeline execution log", "Recent rows are read from SQLite.", "simulation")
    if st.button("Refresh", key="sim_refresh"):
        st.rerun()

    interactions = get_recent_interactions(60)
    if not interactions:
        st.info("No interactions yet. Run the Chatbot Arena tests first.")
        return
    lines = [console_line("--:--:--", "info", "orchestrator: SQLite-backed live trace")]
    for row in reversed(interactions[-30:]):
        ts = str(row.get("timestamp", ""))[11:19]
        action = row.get("defender_action", "?")
        family = row.get("threat_family", "?")
        score = float(row.get("defense_score") or 0)
        ok = not bool(row.get("attack_succeeded", 0))
        lines.append(console_line(ts, "ok" if ok else "bad", f"{family} -> {action} score={score:.2f}"))
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<span class="eyebrow">Cyber Console - Real Pipeline</span>', unsafe_allow_html=True)
        st.markdown(console_block(lines), unsafe_allow_html=True)
    with right:
        metrics = get_metrics()
        attacks = max(metrics.get("attacks_attempted", 0), 1)
        st.markdown(
            f"""
<div class="glass">
  <span class="eyebrow">Real Metrics - From SQLite</span>
  <h3>Live summary</h3>
  <div class="arch-state-grid">
    <div><small>INTERACTIONS</small><br><b style="font-size:1.5rem;">{metrics.get("total_interactions", 0)}</b></div>
    <div><small>AVG DEFENSE</small><br><b style="font-size:1.5rem;color:#00e5ff;">{metrics.get("avg_defense_score", 0):.3f}</b></div>
    <div><small>ATTACK SUCCESS</small><br><b style="font-size:1.5rem;color:#ff4d4d;">{metrics.get("attacks_succeeded", 0) / attacks:.1%}</b></div>
    <div><small>DEFENSE SUCCESS</small><br><b style="font-size:1.5rem;color:#22ff88;">{metrics.get("attacks_blocked", 0) / attacks:.1%}</b></div>
    <div><small>FALSE POSITIVES</small><br><b style="font-size:1.5rem;color:#f97316;">{metrics.get("false_positives", 0)}</b></div>
    <div><small>LEARNED PATTERNS</small><br><b style="font-size:1.5rem;color:#22ff88;">{metrics.get("learned_patterns_count", 0)}</b></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.plotly_chart(action_distribution_chart(pd.DataFrame(interactions)), use_container_width=True)
