import pandas as pd
import plotly.express as px
import streamlit as st

from ui.components import metric_story_card
from ui.layout import render_section_header
from utils.chatbot_engine import get_metrics, get_recent_interactions
from visualizations.charts import PLOT_LAYOUT


METRICS = [
    ("M1", "Attack Success Rate", "Share of threat attempts that produced a leak or bypass."),
    ("M2", "Defense Success Rate", "Share of threat attempts blocked by the Defender."),
    ("M3", "Defense Score", "Evaluator score from 0.0 to 1.0."),
    ("M4", "Adaptation", "Whether repeated patterns are recognized from memory."),
    ("M5", "False Positives", "Benign requests blocked incorrectly."),
    ("M6", "Convergence", "Stability of scores over recent interactions."),
]


def render_evaluation_section() -> None:
    render_section_header("09", "Evaluation", "Live evaluation metrics", "Charts are generated from persisted interactions.", "evaluation")
    metrics = get_metrics()
    rows = get_recent_interactions(500)
    df = pd.DataFrame(rows)

    c = st.columns(6)
    attacks = max(metrics.get("attacks_attempted", 0), 1)
    total = max(metrics.get("total_interactions", 0), 1)
    c[0].metric("Interactions", metrics.get("total_interactions", 0))
    c[1].metric("Attack Success", f"{metrics.get('attacks_succeeded', 0) / attacks:.1%}")
    c[2].metric("Defense Success", f"{metrics.get('attacks_blocked', 0) / attacks:.1%}")
    c[3].metric("Avg Defense", f"{metrics.get('avg_defense_score', 0):.3f}")
    c[4].metric("False Positive", f"{metrics.get('false_positives', 0) / total:.1%}")
    c[5].metric("Patterns", metrics.get("learned_patterns_count", 0))

    if df.empty:
        st.info("No interactions yet. Run tests in the Chatbot Arena.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp").reset_index(drop=True)
        df["interaction"] = range(1, len(df) + 1)
        df["defense_score"] = pd.to_numeric(df["defense_score"], errors="coerce").fillna(0)
        df["attack_succeeded"] = pd.to_numeric(df["attack_succeeded"], errors="coerce").fillna(0)
        left, right = st.columns(2)
        with left:
            fig = px.line(df, x="interaction", y="defense_score", title="Defense score history")
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            counts = df["defender_action"].value_counts().reset_index()
            counts.columns = ["action", "count"]
            fig = px.bar(counts, x="action", y="count", color="action", title="Defender action distribution")
            fig.update_layout(**PLOT_LAYOUT, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.tail(30).sort_values("interaction", ascending=False), use_container_width=True)

    with st.expander("Metric definitions"):
        st.markdown('<div class="metric-grid">' + "".join(metric_story_card(*m) for m in METRICS) + "</div>", unsafe_allow_html=True)
