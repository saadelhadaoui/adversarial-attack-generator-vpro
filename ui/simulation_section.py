import pandas as pd
import streamlit as st

from ui.components import console_block, console_line
from ui.layout import render_section_header
from utils.chatbot_engine import get_metrics, get_recent_interactions
from visualizations.charts import action_distribution_chart


def render_simulation_section() -> None:
    render_section_header("05", "Simulation", "Real pipeline execution log", "Recent rows are read from SQLite.", "simulation")
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
        st.markdown(console_block(lines), unsafe_allow_html=True)
    with right:
        st.json(get_metrics())
        st.plotly_chart(action_distribution_chart(pd.DataFrame(interactions)), use_container_width=True)
