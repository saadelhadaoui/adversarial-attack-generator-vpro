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


def _prepare_interactions(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["interaction"] = range(1, len(df) + 1)
    for col in ["defense_score", "risk_score", "attack_succeeded", "false_positive"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["rolling_defense_score"] = df["defense_score"].rolling(5, min_periods=1).mean()
    df["rolling_attack_success"] = df["attack_succeeded"].rolling(5, min_periods=1).mean() * 100
    df["rolling_false_positive"] = df["false_positive"].rolling(5, min_periods=1).mean() * 100
    return df


def render_evaluation_section() -> None:
    render_section_header(
        "09",
        "Evaluation",
        "Live evaluation metrics",
        "Charts are computed from recorded interactions in data/defense_lab.db.",
        "evaluation",
    )

    if st.button("Refresh Evaluation", key="evaluation_refresh"):
        st.rerun()

    metrics = get_metrics()
    df = _prepare_interactions(get_recent_interactions(500))

    attacks = max(metrics.get("attacks_attempted", 0), 1)
    total = max(metrics.get("total_interactions", 0), 1)
    columns = st.columns(6)
    columns[0].metric("Interactions", metrics.get("total_interactions", 0))
    columns[1].metric("Attack Success", f"{metrics.get('attacks_succeeded', 0) / attacks:.1%}")
    columns[2].metric("Defense Success", f"{metrics.get('attacks_blocked', 0) / attacks:.1%}")
    columns[3].metric("Avg Defense", f"{metrics.get('avg_defense_score', 0):.3f}")
    columns[4].metric("False Positive", f"{metrics.get('false_positives', 0) / total:.1%}")
    columns[5].metric("Learned Patterns", metrics.get("learned_patterns_count", 0))

    if df.empty:
        st.info("No evaluation history yet. Run Chatbot Arena tests to generate database rows.")
    else:
        left, right = st.columns(2)
        with left:
            fig = px.line(
                df,
                x="interaction",
                y=["defense_score", "rolling_defense_score"],
                title="Defense score history",
                labels={"value": "Score", "variable": "Metric", "interaction": "Interaction #"},
            )
            fig.add_hline(y=0.95, line_dash="dash", line_color="#22C55E")
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with right:
            fig = px.line(
                df,
                x="interaction",
                y=["rolling_attack_success", "rolling_false_positive"],
                title="Rolling attack success vs false positives",
                labels={"value": "Rate (%)", "variable": "Metric", "interaction": "Interaction #"},
            )
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        left, right = st.columns(2)
        with left:
            action_counts = df["defender_action"].fillna("unknown").value_counts().reset_index()
            action_counts.columns = ["action", "count"]
            fig = px.bar(
                action_counts,
                x="action",
                y="count",
                color="action",
                title="Defender action distribution",
                color_discrete_map={
                    "BLOCK": "#FF4D4D",
                    "PASS": "#22C55E",
                    "REFORMULATE": "#F97316",
                    "ALLOW_WITH_MONITORING": "#00E5FF",
                },
            )
            fig.update_layout(**PLOT_LAYOUT, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with right:
            threat_df = df[df["threat_family"].fillna("benign") != "benign"]
            if threat_df.empty:
                st.info("No threat-family rows yet. Run the manual or live defense tests first.")
            else:
                family = (
                    threat_df.groupby("threat_family", as_index=False)
                    .agg(
                        attempts=("interaction", "count"),
                        successes=("attack_succeeded", "sum"),
                        avg_defense=("defense_score", "mean"),
                    )
                )
                family["success_rate"] = family["successes"] / family["attempts"].clip(lower=1)
                fig = px.bar(
                    family,
                    x="threat_family",
                    y="success_rate",
                    color="avg_defense",
                    title="Attack success by threat family",
                    color_continuous_scale=["#FF4D4D", "#F97316", "#22C55E"],
                    hover_data=["attempts", "avg_defense"],
                )
                fig.update_yaxes(tickformat=".0%")
                fig.update_layout(**PLOT_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Latest Evaluation Rows")
        display_cols = [
            col
            for col in [
                "timestamp",
                "mode",
                "threat_family",
                "defender_action",
                "risk_score",
                "defense_score",
                "attack_succeeded",
                "false_positive",
                "evaluation_reason",
            ]
            if col in df.columns
        ]
        st.dataframe(
            df.sort_values("interaction", ascending=False)[display_cols].head(25),
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Metric Definitions"):
        st.markdown(
            '<div class="metric-grid">' + "".join(metric_story_card(*metric) for metric in METRICS) + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="glass" style="margin-top:1.5rem;">
  <span class="eyebrow">Philosophy</span>
  <h3>A defense is not a wall. It is a judgment.</h3>
  <p>
    A good defender stays useful while becoming safer. That is why false positives are charted
    beside attack success: blocking everything would look safe, but it would not be a usable assistant.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
