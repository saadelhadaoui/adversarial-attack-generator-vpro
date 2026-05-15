import pandas as pd
import plotly.express as px


PLOT_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#EAF3FF",
    "title_font_color": "#F6FBFF",
    "legend": {"font": {"color": "#EAF3FF", "size": 12}},
    "xaxis": {
        "title_font": {"color": "#EAF3FF", "size": 13},
        "tickfont": {"color": "#D7E4F4", "size": 12},
        "gridcolor": "rgba(215, 228, 244, .22)",
        "zerolinecolor": "rgba(215, 228, 244, .35)",
        "linecolor": "rgba(215, 228, 244, .30)",
    },
    "yaxis": {
        "title_font": {"color": "#EAF3FF", "size": 13},
        "tickfont": {"color": "#D7E4F4", "size": 12},
        "gridcolor": "rgba(215, 228, 244, .22)",
        "zerolinecolor": "rgba(215, 228, 244, .35)",
        "linecolor": "rgba(215, 228, 244, .30)",
    },
    "coloraxis": {
        "colorbar": {
            "title": {"font": {"color": "#EAF3FF"}},
            "tickfont": {"color": "#D7E4F4"},
        }
    },
    "margin": {"l": 60, "r": 28, "t": 70, "b": 62},
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
