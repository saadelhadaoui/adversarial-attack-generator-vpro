import pandas as pd
import plotly.express as px


PLOT_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#E5E7EB",
}


def empty_chart(message: str = "No data yet"):
    fig = px.scatter(pd.DataFrame({"x": [0], "y": [0]}), x="x", y="y", title=message)
    fig.update_traces(marker_opacity=0)
    fig.update_layout(**PLOT_LAYOUT)
    return fig


def defense_score_chart(df: pd.DataFrame):
    if df.empty:
        return empty_chart()
    fig = px.line(df, x="interaction", y="defense_score", title="Defense score")
    fig.update_layout(**PLOT_LAYOUT)
    return fig


def action_distribution_chart(df: pd.DataFrame):
    if df.empty or "defender_action" not in df:
        return empty_chart()
    counts = df["defender_action"].value_counts().reset_index()
    counts.columns = ["action", "count"]
    fig = px.bar(counts, x="action", y="count", color="action", title="Defender actions")
    fig.update_layout(**PLOT_LAYOUT, showlegend=False)
    return fig
