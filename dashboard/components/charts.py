"""PressureIQ Interactive Plotly Visualizations Component.

Provides consistent, dark-themed, publication-quality Plotly charts for rankings,
radar comparisons, bootstrap confidence intervals, and pressure distributions.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils.constants import (
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_PURPLE,
    COLOR_SUCCESS_GREEN,
    COLOR_WARNING_AMBER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    PRESSURE_TIER_COLORS,
    PLOTLY_LAYOUT_DEFAULTS,
)


def render_ranking_bar_chart(
    df: pd.DataFrame,
    role: str = "batting",
    top_n: int = 10,
) -> go.Figure:
    """Create interactive horizontal bar chart with confidence interval error bars."""
    is_batting = role.lower() == "batting"
    rating_col = "final_fbpr" if is_batting else "final_fbor"
    ci_low_col = "ci_lower_fbpr" if is_batting else "ci_lower_fbor"
    ci_upp_col = "ci_upper_fbpr" if is_batting else "ci_upper_fbor"
    title_text = "Top Batters by Final Pressure Rating (FBPR)" if is_batting else "Top Bowlers by Final Pressure Rating (FBOR)"

    if df.empty or rating_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No players match the current filter criteria",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#9CA3AF"),
        )
        fig.update_layout(PLOTLY_LAYOUT_DEFAULTS)
        return fig

    subset = df.head(top_n).copy()
    if subset.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No players match the current filter criteria",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#9CA3AF"),
        )
        fig.update_layout(PLOTLY_LAYOUT_DEFAULTS)
        return fig

    # Reverse order so #1 is at top of vertical axis
    subset = subset.iloc[::-1]

    # Calculate asymmetric error bars safely
    if ci_upp_col in subset.columns and ci_low_col in subset.columns:
        error_plus = subset[ci_upp_col] - subset[rating_col]
        error_minus = subset[rating_col] - subset[ci_low_col]
        error_dict = dict(
            type="data",
            symmetric=False,
            array=error_plus,
            arrayminus=error_minus,
            color="#E2E8F0",
            thickness=1.5,
            width=4,
        )
    else:
        error_dict = None

    fig = go.Figure()

    bar_kwargs = dict(
        y=subset["player_name"],
        x=subset[rating_col],
        orientation="h",
        text=[f"#{int(r)} | {v:.2f}" for r, v in zip(subset.get("rank", range(1, len(subset) + 1)), subset[rating_col])],
        textposition="auto",
        marker=dict(
            color=subset[rating_col],
            colorscale="Viridis" if is_batting else "Plasma",
            showscale=False,
            line=dict(color="#1E293B", width=1),
        ),
        hovertemplate="<b>%{y}</b><br>Rating: %{x:.2f}<extra></extra>",
    )
    if error_dict:
        bar_kwargs["error_x"] = error_dict

    # Attach rich hover data if all components exist
    if all(c in subset.columns for c in ["rank", ci_low_col, ci_upp_col]):
        rate_col = "strike_rate" if is_batting else "economy_rate"
        balls_col = "balls_faced" if is_batting else "legal_balls_bowled"
        if rate_col in subset.columns and balls_col in subset.columns:
            bar_kwargs["customdata"] = np.stack((
                subset["rank"],
                subset[ci_low_col],
                subset[ci_upp_col],
                subset[rate_col],
                subset[balls_col] if is_batting else (subset[balls_col] / 6.0).round(1),
            ), axis=-1)
            bar_kwargs["hovertemplate"] = (
                "<b>%{y}</b> (Rank #%{customdata[0]})<br>"
                + f"{'FBPR' if is_batting else 'FBOR'}: %{{x:.2f}}<br>"
                + "95% CI: [%{customdata[1]:.1f}, %{customdata[2]:.1f}]<br>"
                + f"{'Strike Rate' if is_batting else 'Economy'}: %{{customdata[3]:.1f}}<br>"
                + f"{'Balls Faced' if is_batting else 'Overs'}: %{{customdata[4]}}<br>"
                + "<extra></extra>"
            )

    fig.add_trace(go.Bar(**bar_kwargs))

    layout = dict(PLOTLY_LAYOUT_DEFAULTS)
    layout.update({
        "title": dict(text=title_text, font=dict(size=16, color=COLOR_TEXT_PRIMARY)),
        "xaxis": dict(title=dict(text="Pressure Rating (0–100)", font=dict(color=COLOR_TEXT_SECONDARY)), gridcolor="#1F2937"),
        "yaxis": dict(title=None, tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY)),
        "height": max(400, top_n * 38),
    })
    fig.update_layout(layout)
    return fig


def render_player_radar_chart(radar_data: List[Dict[str, Any]], title: str = "Multi-Dimensional Profile") -> go.Figure:
    """Render multi-player normalized radar comparison chart."""
    fig = go.Figure()

    colors = [COLOR_ACCENT_BLUE, COLOR_ACCENT_PURPLE, COLOR_SUCCESS_GREEN, COLOR_WARNING_AMBER]

    for idx, p in enumerate(radar_data):
        metrics = p["metrics"]
        categories = list(metrics.keys())
        values = list(metrics.values())

        # Close the loop on polar chart
        categories.append(categories[0])
        values.append(values[0])

        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                name=p["player_name"],
                fill="toself",
                fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)",
                line=dict(color=color, width=2),
            )
        )

    layout = dict(PLOTLY_LAYOUT_DEFAULTS)
    layout.update({
        "title": dict(text=title, font=dict(size=15, color=COLOR_TEXT_PRIMARY)),
        "polar": dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1F2937", tickfont=dict(color=COLOR_TEXT_SECONDARY, size=9)),
            angularaxis=dict(gridcolor="#1F2937", tickfont=dict(color=COLOR_TEXT_PRIMARY, size=11)),
            bgcolor="rgba(17,24,39,0.7)",
        ),
        "showlegend": True,
        "legend": dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=COLOR_TEXT_PRIMARY)),
        "height": 450,
    })
    fig.update_layout(layout)
    return fig


def render_baseline_comparison_bar(dossier: Dict[str, Any]) -> go.Figure:
    """Create grouped bar chart comparing performance across baseline and pressure tiers."""
    r = dossier.get("rating_record", {})
    is_batting = dossier.get("role") == "Batter"

    categories = ["Normal Baseline", "Low Pressure", "High Pressure"]
    if is_batting:
        values = [
            float(r.get("overall_strike_rate", 120.0)),
            float(r.get("lp_strike_rate", 125.0)),
            float(r.get("strike_rate", 140.0)),
        ]
        metric_name = "Strike Rate"
    else:
        values = [
            float(r.get("overall_economy_rate", 8.5)),
            float(r.get("lp_economy_rate", 8.0)),
            float(r.get("economy_rate", 9.2)),
        ]
        metric_name = "Economy Rate"

    fig = go.Figure()
    bar_colors = ["#64748B", "#06B6D4", "#EF4444"]

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=bar_colors,
            text=[f"{v:.1f}" for v in values],
            textposition="auto",
        )
    )

    layout = dict(PLOTLY_LAYOUT_DEFAULTS)
    layout.update({
        "title": dict(text=f"{dossier.get('player_name')} — {metric_name} Across Pressure Contexts", font=dict(size=14, color=COLOR_TEXT_PRIMARY)),
        "yaxis": dict(title=metric_name, gridcolor="#1F2937"),
        "height": 320,
    })
    fig.update_layout(layout)
    return fig


def render_pressure_distribution_pie(tier_counts: Dict[str, int]) -> go.Figure:
    """Render donut chart of deliveries across pressure tiers."""
    labels = list(tier_counts.keys())
    values = list(tier_counts.values())
    colors = [PRESSURE_TIER_COLORS.get(lbl, "#6B7280") for lbl in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#0B0F19", width=2)),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )
        ]
    )

    layout = dict(PLOTLY_LAYOUT_DEFAULTS)
    layout.update({
        "title": dict(text="Ball-by-Ball Delivery Pressure Distribution (200,999 Deliveries)", font=dict(size=15, color=COLOR_TEXT_PRIMARY)),
        "showlegend": True,
        "legend": dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        "height": 380,
    })
    fig.update_layout(layout)
    return fig


def render_bootstrap_distribution(boot_row: Dict[str, Any], role: str = "batting") -> go.Figure:
    """Render normal/empirical distribution curve with 90% and 95% CI bands."""
    is_batting = role.lower() == "batting"
    mean_val = float(boot_row.get("bootstrap_mean_fbpr" if is_batting else "bootstrap_mean_fbor", 50.0))
    std_val = float(boot_row.get("bootstrap_std_fbpr" if is_batting else "bootstrap_std_fbor", 4.0))
    ci95_l = float(boot_row.get("ci_95_lower", mean_val - 1.96 * std_val))
    ci95_u = float(boot_row.get("ci_95_upper", mean_val + 1.96 * std_val))
    off_val = float(boot_row.get("official_fbpr" if is_batting else "official_fbor", mean_val))

    x_vals = np.linspace(mean_val - 4 * std_val, mean_val + 4 * std_val, 200)
    y_vals = (1.0 / (std_val * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_vals - mean_val) / std_val) ** 2)

    fig = go.Figure()

    # Main density curve
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line=dict(color=COLOR_ACCENT_BLUE, width=2.5),
            name="Bootstrap PDF",
        )
    )

    # Shaded 95% CI
    ci_mask = (x_vals >= ci95_l) & (x_vals <= ci95_u)
    fig.add_trace(
        go.Scatter(
            x=np.concatenate(([ci95_l], x_vals[ci_mask], [ci95_u])),
            y=np.concatenate(([0], y_vals[ci_mask], [0])),
            fill="toself",
            fillcolor="rgba(56, 189, 248, 0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="95% CI Band",
            hoverinfo="skip",
        )
    )

    # Official rating vertical marker
    fig.add_vline(
        x=off_val,
        line_width=2,
        line_dash="dash",
        line_color=COLOR_SUCCESS_GREEN,
        annotation_text=f"Official: {off_val:.2f}",
        annotation_position="top right",
    )

    layout = dict(PLOTLY_LAYOUT_DEFAULTS)
    layout.update({
        "title": dict(
            text=f"{boot_row.get('player_name', 'Player')} — 100-Sample Match Block Bootstrap Distribution",
            font=dict(size=14, color=COLOR_TEXT_PRIMARY),
        ),
        "xaxis": dict(title="Rating Points", gridcolor="#1F2937"),
        "yaxis": dict(title="Density", showticklabels=False),
        "height": 320,
    })
    fig.update_layout(layout)
    return fig

