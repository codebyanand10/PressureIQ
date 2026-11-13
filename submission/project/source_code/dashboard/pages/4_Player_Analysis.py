"""PressureIQ Page 4: Individual Player Analysis Dossier.

Deep-dive player profile featuring dual-role toggles, 10-metric KPI grids,
baseline comparisons across pressure tiers, Phase 8 narrative rationales,
and Phase 9 bootstrap uncertainty distributions.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.header import render_header
from dashboard.components.sidebar import render_sidebar
from dashboard.components.player_profile import (
    render_player_header,
    render_batter_stats_grid,
    render_bowler_stats_grid,
    render_player_explanation_callout,
)
from dashboard.components.charts import (
    render_baseline_comparison_bar,
    render_bootstrap_distribution,
)
from dashboard.components.download_buttons import render_csv_download
from dashboard.services.player_service import get_all_player_names_and_ids, get_player_dossier
from dashboard.utils.formatting import format_number, format_pct, format_ci, format_rank


def main() -> None:
    st.set_page_config(page_title="Player Analysis | PressureIQ", page_icon="👤", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Individual Player Analysis Dossier")

    players = get_all_player_names_and_ids()
    if not players:
        st.error("No player records available in dataset.")
        return

    # Player Selector
    player_options = {p["display_label"]: p for p in players}
    # Default to Rinku Singh or first player
    default_idx = 0
    for i, label in enumerate(player_options.keys()):
        if "Rinku Singh" in label:
            default_idx = i
            break

    sel_col1, sel_col2 = st.columns([3, 1])

    with sel_col1:
        selected_label = st.selectbox(
            "Select Player",
            options=list(player_options.keys()),
            index=default_idx,
            help="Choose any evaluated batter or bowler to inspect their full pressure profile.",
        )

    selected_player = player_options[selected_label]
    pid = selected_player["player_id"]
    has_bat = selected_player["has_batting"]
    has_bowl = selected_player["has_bowling"]

    with sel_col2:
        if has_bat and has_bowl:
            role_choice = st.radio("Active Profile Mode", ["Batting", "Bowling"], horizontal=True)
            active_role = role_choice.lower()
        elif has_bat:
            active_role = "batting"
            st.info("Role: Batter")
        else:
            active_role = "bowling"
            st.info("Role: Bowler")

    # Load full dossier
    dossier = get_player_dossier(pid, role=active_role)
    if not dossier:
        st.warning("Could not assemble complete player profile.")
        return

    # 1. Profile Header
    render_player_header(dossier)

    # 2. Key Metrics Grid
    r = dossier.get("rating_record", {})
    st.markdown("### 📊 High-Pressure Performance Statistics")
    if active_role == "batting":
        render_batter_stats_grid(r)
    else:
        render_bowler_stats_grid(r)

    st.markdown("---")

    # 3. Baseline Comparison & Bootstrap Uncertainty Tabs
    tab_base, tab_uncert, tab_sit = st.tabs([
        "⚖️ Baseline vs Pressure Comparison",
        "🛡️ Phase 9 Bootstrap Uncertainty",
        "📍 Situational & Category Breakdown",
    ])

    with tab_base:
        col_b1, col_b2 = st.columns([3, 2])
        with col_b1:
            fig_base = render_baseline_comparison_bar(dossier)
            st.plotly_chart(fig_base, use_container_width=True)
        with col_b2:
            st.markdown("#### Baseline Retention Analysis")
            if active_role == "batting":
                sr_diff = r.get("strike_rate_difference", 0.0)
                st.write(f"• **Baseline Strike Rate:** {format_number(r.get('overall_strike_rate'), 1)}")
                st.write(f"• **High-Pressure Strike Rate:** {format_number(r.get('strike_rate'), 1)}")
                st.write(f"• **Scoring Rate Retention:** {format_pct(r.get('strike_rate_retention'), 1)}")
                st.write(f"• **Net SR Shift:** {'+' if sr_diff > 0 else ''}{sr_diff:.1f} runs / 100 balls")
                st.write(f"• **BPPI Resilience Score:** {format_number(r.get('bppi'), 1)} / 100")
            else:
                econ_diff = r.get("economy_difference", 0.0)
                st.write(f"• **Baseline Economy:** {format_number(r.get('overall_economy_rate'), 2)} rpo")
                st.write(f"• **High-Pressure Economy:** {format_number(r.get('economy_rate'), 2)} rpo")
                st.write(f"• **Containment Retention:** {format_pct(r.get('economy_retention'), 1)}")
                st.write(f"• **Net Economy Shift:** {'+' if econ_diff > 0 else ''}{econ_diff:.2f} rpo")
                st.write(f"• **BPPI-B Resilience Score:** {format_number(r.get('bppi_b'), 1)} / 100")

    with tab_uncert:
        boot_data = dossier.get("bootstrap_data", {})
        stab_data = dossier.get("stability_data", {})
        if boot_data:
            col_u1, col_u2 = st.columns([3, 2])
            with col_u1:
                fig_boot = render_bootstrap_distribution(boot_data, role=active_role)
                st.plotly_chart(fig_boot, use_container_width=True)
            with col_u2:
                st.markdown("#### 100-Resample Empirical Stability")
                st.write(f"• **Official Rank:** #{int(boot_data.get('official_rank', 0))}")
                st.write(f"• **Median Bootstrap Rank:** #{int(boot_data.get('median_bootstrap_rank', 0))}")
                st.write(f"• **Best / Worst Resample Rank:** #{int(boot_data.get('best_bootstrap_rank', 0))} / #{int(boot_data.get('worst_bootstrap_rank', 0))}")
                st.write(f"• **P(Rank in Top 10):** {boot_data.get('prob_in_top_10', 0.0) * 100:.1f}%")
                st.write(f"• **P(Rank in Top 5):** {boot_data.get('prob_in_top_5', 0.0) * 100:.1f}%")
                st.write(f"• **LOMO Max Rank Drop:** {stab_data.get('max_rank_drop_lomo', 0)} ranks")
                st.write(f"• **Stability Class:** `{stab_data.get('stability_classification', 'STABLE')}`")
        else:
            st.info("Bootstrap uncertainty distribution not calculated for this candidate.")

    with tab_sit:
        cats_df = dossier.get("category_metrics", pd.DataFrame())
        sit_df = dossier.get("situational_metrics", pd.DataFrame())

        if not cats_df.empty:
            st.markdown("#### Performance by Pressure Category Tier")
            st.dataframe(cats_df, use_container_width=True, hide_index=True)
        else:
            st.info("Category metrics across individual pressure tiers not available.")

        if not sit_df.empty:
            st.markdown("#### Performance by Innings Phase & Situational State")
            st.dataframe(sit_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 4. Official Explanation Narrative Callout
    render_player_explanation_callout(r)

    st.markdown("---")

    # 5. Export Individual Dossier
    st.markdown("### 📥 Export Player Dossier")
    single_df = pd.DataFrame([r])
    render_csv_download(
        single_df,
        filename=f"PressureIQ_Dossier_{dossier.get('player_name', 'Player').replace(' ', '_')}.csv",
        label=f"📥 Download {dossier.get('player_name')} Statistical Dossier (CSV)",
    )


if __name__ == "__main__":
    main()

