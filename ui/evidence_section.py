import pandas as pd
import plotly.express as px
import streamlit as st

from ui.layout import render_section_header
from utils.chatbot_engine import get_recent_interactions
from visualizations.charts import PLOT_LAYOUT


def render_evidence_section() -> None:
    render_section_header("06", "Evidence", "Proof that the system adapts", "The charts below come from real interaction rows.", "evidence")
    df = pd.DataFrame(get_recent_interactions(200))
    if df.empty:
        st.info("No evidence yet. Run the Live Defense Run sequence.")
        return
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["interaction"] = range(1, len(df) + 1)
    df["defense_score"] = pd.to_numeric(df["defense_score"], errors="coerce").fillna(0)
    df["attack_succeeded"] = pd.to_numeric(df["attack_succeeded"], errors="coerce").fillna(0)
    left, right = st.columns(2)
    with left:
        fig = px.line(df, x="interaction", y="defense_score", title="Defense score over time")
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(df, x="interaction", y="attack_succeeded", title="Attack success by interaction")
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
