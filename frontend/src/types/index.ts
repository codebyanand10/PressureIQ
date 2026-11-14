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

export interface OverviewData {
  macro_telemetry: {
    total_deliveries: number;
    matches_analyzed: number;
    high_pressure_deliveries: number;
    extreme_pressure_deliveries: number;
    high_pressure_percentage: number;
    evaluated_batters: number;
    evaluated_bowlers: number;
    eligible_batters: number;
    eligible_bowlers: number;
  };
  pressure_tier_distribution: Record<string, number>;
  clutch_highlights: {
    batting: {
      player_name: string;
      final_fbpr: number;
      strike_rate: number;
      high_pressure_balls: number;
      explanation: string;
    };
    bowling: {
      player_name: string;
      final_fbor: number;
      economy_rate: number;
      wickets: number;
      explanation: string;
    };
  };
}

export interface ValidationData {
  scorecard: Array<{
    dimension: string;
    description: string;
    status: 'PASS' | 'WARN' | 'FAIL';
    finding: string;
    metric_value: string;
  }>;
  leakage_audit: Array<{
    check: string;
    scope: string;
    status: 'PASS' | 'WARN' | 'FAIL';
    details: string;
  }>;
}

export interface MethodologyData {
  bimodal_pressure: {
    description: string;
    chase_components: string[];
    first_innings_components: string[];
    weights: {
      chase: Record<string, number>;
      first_innings: Record<string, number>;
    };
  };
  rating_engines: {
    fbpr: {
      name: string;
      formula: string;
      weights: Record<string, number>;
    };
    fbor: {
      name: string;
      formula: string;
      weights: Record<string, number>;
    };
  };
}

export interface DataQualityData {
  pipeline_telemetry: {
    raw_balls: number;
    processed_deliveries: number;
    unique_matches: number;
    unique_players: number;
    cardinality_reconciliation: string;
  };
  physics_invariants: Array<{
    invariant: string;
    expected: string;
    actual: string;
    status: 'PASS' | 'FAIL';
  }>;
}
