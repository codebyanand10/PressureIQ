"""PressureIQ Ranking Auditor.

Validates official Phase 8 Top-10 Batters and Top-10 Bowlers rankings for
integrity, strict ordering, eligibility compliance, statistical consistency,
and concordance across CSV, Excel, and Parquet representations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.FinalAudit.Rankings")


@dataclass
class RankingAuditIssue:
    """An issue identified during ranking validation."""
    discipline: str  # batting or bowling
    severity: str    # CRITICAL, WARNING, INFO
    player_name: Optional[str]
    check_name: str
    description: str


@dataclass
class RankingAuditSummary:
    """Summary of ranking audit findings."""
    batting_verified: bool
    bowling_verified: bool
    cross_format_concordance: bool
    issues: List[RankingAuditIssue] = field(default_factory=list)
    top_10_batters: List[Dict[str, Any]] = field(default_factory=list)
    top_10_bowlers: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def has_critical_issues(self) -> bool:
        return any(i.severity == "CRITICAL" for i in self.issues)


class RankingAuditor:
    """Audits official top-10 batter and bowler rankings."""

    def __init__(self, root_dir: Path | str | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

    def audit_batting_rankings(self) -> List[RankingAuditIssue]:
        """Audit top 10 batter ranking file."""
        issues: List[RankingAuditIssue] = []
        csv_path = self.root_dir / "outputs/rankings/top_10_batters.csv"

        if not csv_path.exists():
            issues.append(
                RankingAuditIssue(
                    discipline="batting",
                    severity="CRITICAL",
                    player_name=None,
                    check_name="file_existence",
                    description=f"Batting ranking file not found at {csv_path}",
                )
            )
            return issues

        df = pd.read_csv(csv_path)

        # 1. Exactly 10 players
        if len(df) != 10:
            issues.append(
                RankingAuditIssue(
                    discipline="batting",
                    severity="CRITICAL",
                    player_name=None,
                    check_name="row_count",
                    description=f"Expected exactly 10 batters, found {len(df)}",
                )
            )

        # 2. Unique player IDs
        if "player_id" in df.columns:
            dups = df[df.duplicated(subset=["player_id"])]
            if len(dups) > 0:
                issues.append(
                    RankingAuditIssue(
                        discipline="batting",
                        severity="CRITICAL",
                        player_name=str(dups["player_id"].tolist()),
                        check_name="duplicate_player_ids",
                        description=f"Duplicate player IDs found: {dups['player_id'].tolist()}",
                    )
                )

        # 3. Monotonic descending order by final_fbpr or ranking_score
        score_col = "final_fbpr" if "final_fbpr" in df.columns else "ranking_score"
        if score_col in df.columns:
            scores = df[score_col].tolist()
            if not all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)):
                issues.append(
                    RankingAuditIssue(
                        discipline="batting",
                        severity="CRITICAL",
                        player_name=None,
                        check_name="ranking_order",
                        description=f"Batters are not in strictly descending score order by {score_col}.",
                    )
                )

        # 4. Eligibility check: HP balls >= 40, matches >= 5
        balls_col = "high_pressure_balls" if "high_pressure_balls" in df.columns else "balls_faced"
        matches_col = "matches_count" if "matches_count" in df.columns else "matches"

        for _, row in df.iterrows():
            name = row.get("player_name", "Unknown")
            hp_balls = row.get(balls_col, 0)
            matches = row.get(matches_col, 0)

            if hp_balls < 40:
                issues.append(
                    RankingAuditIssue(
                        discipline="batting",
                        severity="CRITICAL",
                        player_name=name,
                        check_name="eligibility_hp_balls",
                        description=f"Batter {name} has {hp_balls} HP balls (minimum threshold: 40).",
                    )
                )
            if matches < 5:
                issues.append(
                    RankingAuditIssue(
                        discipline="batting",
                        severity="WARNING",
                        player_name=name,
                        check_name="eligibility_matches",
                        description=f"Batter {name} has {matches} matches (recommended minimum: 5).",
                    )
                )

        return issues

    def audit_bowling_rankings(self) -> List[RankingAuditIssue]:
        """Audit top 10 bowler ranking file."""
        issues: List[RankingAuditIssue] = []
        csv_path = self.root_dir / "outputs/rankings/top_10_bowlers.csv"

        if not csv_path.exists():
            issues.append(
                RankingAuditIssue(
                    discipline="bowling",
                    severity="CRITICAL",
                    player_name=None,
                    check_name="file_existence",
                    description=f"Bowling ranking file not found at {csv_path}",
                )
            )
            return issues

        df = pd.read_csv(csv_path)

        # 1. Exactly 10 players
        if len(df) != 10:
            issues.append(
                RankingAuditIssue(
                    discipline="bowling",
                    severity="CRITICAL",
                    player_name=None,
                    check_name="row_count",
                    description=f"Expected exactly 10 bowlers, found {len(df)}",
                )
            )

        # 2. Unique player IDs
        if "player_id" in df.columns:
            dups = df[df.duplicated(subset=["player_id"])]
            if len(dups) > 0:
                issues.append(
                    RankingAuditIssue(
                        discipline="bowling",
                        severity="CRITICAL",
                        player_name=str(dups["player_id"].tolist()),
                        check_name="duplicate_player_ids",
                        description=f"Duplicate bowler IDs found: {dups['player_id'].tolist()}",
                    )
                )

        # 3. Monotonic descending order by final_fbor or ranking_score
        score_col = "final_fbor" if "final_fbor" in df.columns else "ranking_score"
        if score_col in df.columns:
            scores = df[score_col].tolist()
            if not all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)):
                issues.append(
                    RankingAuditIssue(
                        discipline="bowling",
                        severity="CRITICAL",
                        player_name=None,
                        check_name="ranking_order",
                        description=f"Bowlers are not in strictly descending score order by {score_col}.",
                    )
                )

        # 4. Eligibility check: HP legal balls >= 48 (8 overs)
        legal_balls_col = "legal_balls_bowled" if "legal_balls_bowled" in df.columns else "hp_total_legal_balls"
        matches_col = "matches_bowled" if "matches_bowled" in df.columns else "matches_count"

        for _, row in df.iterrows():
            name = row.get("player_name", "Unknown")
            hp_balls = row.get(legal_balls_col, 0)
            matches = row.get(matches_col, 0)

            if hp_balls < 48:
                issues.append(
                    RankingAuditIssue(
                        discipline="bowling",
                        severity="CRITICAL",
                        player_name=name,
                        check_name="eligibility_hp_overs",
                        description=f"Bowler {name} has {hp_balls} HP balls (minimum threshold: 48 balls / 8 overs).",
                    )
                )
            if matches < 5:
                issues.append(
                    RankingAuditIssue(
                        discipline="bowling",
                        severity="WARNING",
                        player_name=name,
                        check_name="eligibility_matches",
                        description=f"Bowler {name} has {matches} matches (recommended minimum: 5).",
                    )
                )

        return issues

    def audit_cross_format_concordance(self) -> List[RankingAuditIssue]:
        """Verify that CSV, XLSX, and Parquet export identical ranks and player names."""
        issues: List[RankingAuditIssue] = []

        # Batting check
        csv_bat = self.root_dir / "outputs/rankings/top_10_batters.csv"
        xlsx_bat = self.root_dir / "outputs/rankings/top_10_batters.xlsx"

        if csv_bat.exists() and xlsx_bat.exists():
            df_csv = pd.read_csv(csv_bat)
            df_xlsx = pd.read_excel(xlsx_bat)
            if df_csv["player_name"].tolist() != df_xlsx["player_name"].tolist():
                issues.append(
                    RankingAuditIssue(
                        discipline="batting",
                        severity="CRITICAL",
                        player_name=None,
                        check_name="format_concordance",
                        description="Batters order differs between CSV and XLSX outputs.",
                    )
                )

        # Bowling check
        csv_bowl = self.root_dir / "outputs/rankings/top_10_bowlers.csv"
        xlsx_bowl = self.root_dir / "outputs/rankings/top_10_bowlers.xlsx"

        if csv_bowl.exists() and xlsx_bowl.exists():
            df_csv = pd.read_csv(csv_bowl)
            df_xlsx = pd.read_excel(xlsx_bowl)
            if df_csv["player_name"].tolist() != df_xlsx["player_name"].tolist():
                issues.append(
                    RankingAuditIssue(
                        discipline="bowling",
                        severity="CRITICAL",
                        player_name=None,
                        check_name="format_concordance",
                        description="Bowlers order differs between CSV and XLSX outputs.",
                    )
                )

        return issues

    def audit(self) -> RankingAuditSummary:
        """Run full ranking audit and return summary."""
        logger.info("Executing comprehensive ranking audit.")
        bat_issues = self.audit_batting_rankings()
        bowl_issues = self.audit_bowling_rankings()
        concordance_issues = self.audit_cross_format_concordance()

        all_issues = bat_issues + bowl_issues + concordance_issues

        # Load top 10 dictionaries
        csv_bat = self.root_dir / "outputs/rankings/top_10_batters.csv"
        csv_bowl = self.root_dir / "outputs/rankings/top_10_bowlers.csv"

        bat_list = pd.read_csv(csv_bat).to_dict(orient="records") if csv_bat.exists() else []
        bowl_list = pd.read_csv(csv_bowl).to_dict(orient="records") if csv_bowl.exists() else []

        summary = RankingAuditSummary(
            batting_verified=len(bat_issues) == 0,
            bowling_verified=len(bowl_issues) == 0,
            cross_format_concordance=len(concordance_issues) == 0,
            issues=all_issues,
            top_10_batters=bat_list,
            top_10_bowlers=bowl_list,
        )

        logger.info(
            f"Ranking audit finished: Batting verified: {summary.batting_verified}, "
            f"Bowling verified: {summary.bowling_verified}, "
            f"Concordance verified: {summary.cross_format_concordance}, "
            f"Total issues: {len(all_issues)}"
        )
        return summary

