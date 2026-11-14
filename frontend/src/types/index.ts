export interface Batter {
  player_id: string;
  player_name: string;
  rank: number;
  final_fbpr: number;
  ranking_score: number;
  raw_fbpr?: number;
  shrinkage_factor?: number;
  ci_lower_fbpr: number;
  ci_upper_fbpr: number;
  ci_width_fbpr: number;
  rating_standard_error?: number;
  
  // Performance Under Pressure
  total_runs: number;
  balls_faced: number;
  dismissals: number;
  strike_rate: number;
  batting_average: number;
  fours: number;
  sixes: number;
  boundary_runs?: number;
  dot_balls: number;
  boundary_percentage: number;
  dot_ball_percentage: number;
  scoring_delivery_percentage?: number;
  dismissal_rate?: number;
  balls_per_dismissal?: number;
  
  // Baselines & Comparison
  overall_strike_rate: number;
  overall_batting_average: number;
  strike_rate_difference: number;
  strike_rate_retention: number;
  average_difference?: number;
  average_retention?: number;
  boundary_percentage_difference?: number;
  dot_ball_difference?: number;
  
  // Scores & Ratings
  score_batting_resilience: number;
  score_batting_absolute: number;
  score_batting_consistency: number;
  score_batting_context: number;
  bppi: number;
  reliability_level: string;
  reliability_score?: number;
  is_statistically_reliable?: boolean;
  batter_classification?: string;
  
  // Exposure & Explanations
  matches_count: number;
  innings_count: number;
  sample_deliveries?: number;
  high_pressure_balls?: number;
  extreme_pressure_balls?: number;
  ranking_explanation: string;
  key_strengths: string;
  baseline_comparison: string;
  reliability_summary: string;
  pressure_exposure: string;
  ranking_limitations?: string;
}

export interface Bowler {
  player_id: string;
  player_name: string;
  rank: number;
  final_fbor: number;
  ranking_score: number;
  raw_fbor?: number;
  shrinkage_factor?: number;
  ci_lower_fbor: number;
  ci_upper_fbor: number;
  ci_width_fbor: number;
  rating_standard_error?: number;
  
  // Performance Under Pressure
  legal_balls_bowled: number;
  runs_conceded: number;
  wickets_credited: number;
  economy_rate: number;
  bowling_average: number;
  bowling_strike_rate: number;
  dot_balls: number;
  fours_conceded: number;
  sixes_conceded: number;
  boundary_runs_conceded?: number;
  dot_ball_percentage: number;
  boundary_percentage_conceded: number;
  overs_bowled: number;
  matches_count: number;
  innings_count: number;
  
  // Baselines & Comparison
  overall_economy_rate: number;
  overall_bowling_average: number;
  overall_bowling_strike_rate: number;
  economy_difference: number;
  economy_retention: number;
  strike_rate_retention?: number;
  dot_ball_difference?: number;
  boundary_concession_difference?: number;
  
  // Roles & Phasing
  bowling_role: string;
  primary_bowling_style: string;
  DEATH_OVERS?: number;
  MIDDLE_OVERS?: number;
  POWERPLAY?: number;
  
  // Scores & Ratings
  score_bowling_resilience: number;
  score_bowling_absolute: number;
  score_bowling_consistency: number;
  score_bowling_context: number;
  bppi_b: number;
  reliability_level: string;
  reliability_score?: number;
  is_statistically_reliable?: boolean;
  bowler_classification?: string;
  
  // Exposure & Explanations
  ranking_explanation: string;
  key_strengths: string;
  baseline_comparison: string;
  reliability_summary: string;
  pressure_exposure: string;
  ranking_limitations?: string;
}

export interface PressureDistributionItem {
  tier: string;
  deliveries: number;
  percentage: number;
  color: string;
}

export interface OverviewData {
  total_matches: number;
  matches_with_deliveries: number;
  total_deliveries: number;
  hp_deliveries: number;
  extreme_pressure_deliveries: number;
  hp_matches: number;
  total_eligible_batters: number;
  total_eligible_bowlers: number;
  total_evaluated_players: number;
  validation_scorecard_pass_rate: string;
  data_leakage_checks_passed: string;
  top_batter: Batter;
  top_bowler: Bowler;
  pressure_distribution: PressureDistributionItem[];
  competition_split?: Record<string, number>;
}

export interface ScorecardItem {
  dimension: string;
  batting_result: string;
  bowling_result: string;
  supporting_evidence: string;
  operational_impact: string;
}

export interface LeakageAuditItem {
  check_id: string;
  test_performed: string;
  data_fields_examined: string;
  result: string;
  severity: string;
  evidence: string;
  required_action: string | null;
}

export interface ValidationData {
  status: string;
  summary: string;
  scorecard: ScorecardItem[];
  leakage_audit: LeakageAuditItem[];
  bootstrap_iterations: number;
  resampling_unit: string;
}

export interface TableStatus {
  name: string;
  records: number;
  status: string;
  size: string;
}

export interface DataQualityData {
  dataset_health: string;
  matches_count: number;
  bowled_matches: number;
  deliveries_count: number;
  duplicate_deliveries: number;
  cricket_physics_violations: number;
  temporal_causality_violations: number;
  tables: TableStatus[];
}
