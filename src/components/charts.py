import plotly.graph_objects as go
import plotly.express as px

COLORS = ["#0D9488", "#14B8A6", "#2DD4BF", "#5EEAD4", "#99F6E4", "#CCFBF1"]


def build_radar_chart(dimensions: dict, title: str = "技能雷达图") -> go.Figure:
    labels = list(dimensions.keys())
    values = list(dimensions.values())
    labels_cn = {
        "completeness": "完整度", "keyword_match": "关键词匹配",
        "quantification": "量化程度", "structure": "结构清晰",
        "language": "语言专业", "competitiveness": "竞争力",
    }
    labels = [labels_cn.get(l, l) for l in labels]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(13, 148, 136, 0.2)",
        line=dict(color=COLORS[0], width=2),
        name="当前评分",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], tickfont=dict(color="#5B8A87"))),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#0F766E"),
        title=dict(text=title, font=dict(color="#0F766E", size=14)),
        margin=dict(t=40, b=20, l=40, r=40),
    )
    return fig


def build_line_chart(data: list, x_key: str, y_keys: list, title: str = "",
                     labels: dict = None) -> go.Figure:
    fig = go.Figure()
    for i, yk in enumerate(y_keys):
        x_vals = [d.get(x_key, "") for d in data]
        y_vals = [d.get(yk) for d in data]
        label = (labels or {}).get(yk, yk) if labels else yk
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode="lines+markers",
            name=label,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            marker=dict(size=6, color=COLORS[i % len(COLORS)]),
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#5B8A87"),
        title=dict(text=title, font=dict(color="#0F766E", size=14)),
        xaxis=dict(gridcolor="#CCFBF1"),
        yaxis=dict(gridcolor="#CCFBF1", range=[0, 100]),
        margin=dict(t=40, b=20, l=30, r=20),
        legend=dict(font=dict(color="#5B8A87")),
    )
    return fig


def build_bar_chart(categories: list, values: list, title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, y=values,
        marker=dict(color=COLORS[0], line=dict(color=COLORS[1], width=1)),
        text=values, textposition="outside",
        textfont=dict(color="#0F766E", size=12),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#5B8A87"),
        title=dict(text=title, font=dict(color="#0F766E", size=14)),
        yaxis=dict(gridcolor="#CCFBF1", range=[0, max(values) + 15 if values else 100]),
        margin=dict(t=40, b=20, l=30, r=20),
    )
    return fig


def build_funnel_chart(stages: list, counts: list, title: str = "求职漏斗") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Funnel(
        y=stages, x=counts,
        textinfo="value+percent initial",
        marker=dict(
            color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4], COLORS[5]][:len(stages)],
            line=dict(width=0),
        ),
        textfont=dict(color="#FFFFFF", size=13),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#5B8A87"),
        title=dict(text=title, font=dict(color="#0F766E", size=14)),
        margin=dict(t=40, b=20, l=30, r=20),
    )
    return fig


def build_score_distribution(scores: list, title: str = "得分分布") -> go.Figure:
    fig = px.histogram(
        x=scores, nbins=5,
        range_x=[0, 100],
        color_discrete_sequence=[COLORS[0]],
        labels={"x": "分数", "y": "次数"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#5B8A87"),
        title=dict(text=title, font=dict(color="#0F766E", size=14)),
        xaxis=dict(gridcolor="#CCFBF1"),
        yaxis=dict(gridcolor="#CCFBF1"),
        margin=dict(t=40, b=20, l=30, r=20),
    )
    return fig


def build_gauge_chart(value: float, title: str = "评分") -> go.Figure:
    color = "#0D9488" if value >= 80 else "#F59E0B" if value >= 60 else "#EF4444"
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=title, font=dict(color="#0F766E")),
        number=dict(font=dict(color=color, size=36)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#5B8A87"),
            bar=dict(color=color, thickness=0.2),
            bgcolor="#F0FDFA",
            borderwidth=1,
            bordercolor="#CCFBF1",
            steps=[
                dict(range=[0, 40], color="#FEE2E2"),
                dict(range=[40, 60], color="#FEF3C7"),
                dict(range=[60, 80], color="#CCFBF1"),
                dict(range=[80, 100], color="#F0FDFA"),
            ],
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"),
        margin=dict(t=40, b=20, l=20, r=20),
        height=250,
    )
    return fig
