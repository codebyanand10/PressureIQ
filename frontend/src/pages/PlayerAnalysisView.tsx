import React, { useState, useMemo } from 'react';
import {
  User,
  Search,
  Award,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Info,
  CheckCircle2,
  Zap,
  Target
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import battersData from '../data/batters.json';
import bowlersData from '../data/bowlers.json';
import { Batter, Bowler } from '../types';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

interface PlayerAnalysisViewProps {
  initialPlayerId?: string;
  onNavigate: (page: PageId) => void;
}

export const PlayerAnalysisView: React.FC<PlayerAnalysisViewProps> = ({
  initialPlayerId,
  onNavigate
}) => {
  const allBatters = battersData as Batter[];
  const allBowlers = bowlersData as Bowler[];

  const [role, setRole] = useState<'batter' | 'bowler'>('batter');
  const [selectedId, setSelectedId] = useState<string>(
    initialPlayerId || allBatters[0]?.player_id || '4708'
  );

  const currentBatter = useMemo(
    () => allBatters.find((b) => b.player_id === selectedId) || allBatters[0],
    [allBatters, selectedId]
  );

  const currentBowler = useMemo(
    () => allBowlers.find((bw) => bw.player_id === selectedId) || allBowlers[0],
    [allBowlers, selectedId]
  );

  // Radar chart data calculation
  const radarData = useMemo(() => {
    if (role === 'batter' && currentBatter) {
      return [
        {
          subject: 'Resilience',
          value: Math.min(100, currentBatter.score_batting_resilience || 75),
          fullMark: 100
        },
        {
          subject: 'Absolute Power',
          value: Math.min(100, currentBatter.score_batting_absolute || 80),
          fullMark: 100
        },
        {
          subject: 'Consistency',
          value: Math.min(100, currentBatter.score_batting_consistency || 65),
          fullMark: 100
        },
        {
          subject: 'Context Clutch',
          value: Math.min(100, currentBatter.score_batting_context || 70),
          fullMark: 100
        },
        {
          subject: 'SR Retention',
          value: Math.min(100, (currentBatter.strike_rate_retention / 2) || 70),
          fullMark: 100
        }
      ];
    } else if (currentBowler) {
      return [
        {
          subject: 'Resilience',
          value: Math.min(100, currentBowler.score_bowling_resilience || 70),
          fullMark: 100
        },
        {
          subject: 'Restriction',
          value: Math.min(100, currentBowler.score_bowling_absolute || 75),
          fullMark: 100
        },
        {
          subject: 'Consistency',
          value: Math.min(100, currentBowler.score_bowling_consistency || 60),
          fullMark: 100
        },
        {
          subject: 'Phase Clutch',
          value: Math.min(100, currentBowler.score_bowling_context || 65),
          fullMark: 100
        },
        {
          subject: 'Dot Pressure',
          value: Math.min(100, currentBowler.dot_ball_percentage * 1.5 || 60),
          fullMark: 100
        }
      ];
    }
    return [];
  }, [role, currentBatter, currentBowler]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Selector Bar */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="inline-flex rounded-xl p-1 bg-[#0E1117] border border-[#21262D]">
            <button
              onClick={() => {
                setRole('batter');
                setSelectedId(allBatters[0]?.player_id || '');
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                role === 'batter'
                  ? 'bg-[#00FFCC] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              <Award size={14} />
              <span>Batters (170)</span>
            </button>
            <button
              onClick={() => {
                setRole('bowler');
                setSelectedId(allBowlers[0]?.player_id || '');
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                role === 'bowler'
                  ? 'bg-[#38BDF8] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              <ShieldCheck size={14} />
              <span>Bowlers (232)</span>
            </button>
          </div>

          <div className="relative">
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="bg-[#0E1117] text-white border border-[#30363D] rounded-xl px-4 py-2 text-xs font-medium focus:outline-none focus:border-[#00FFCC] cursor-pointer"
            >
              {role === 'batter'
                ? allBatters.map((b) => (
                    <option key={b.player_id} value={b.player_id}>
                      #{b.rank} {b.player_name} (FBPR: {b.final_fbpr.toFixed(1)})
                    </option>
                  ))
                : allBowlers.map((bw) => (
                    <option key={bw.player_id} value={bw.player_id}>
                      #{bw.rank} {bw.player_name} (FBOR: {bw.final_fbor.toFixed(1)})
                    </option>
                  ))}
            </select>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs text-[#8B949E]">
          <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
          <span>Verified empirical Bayes shrinkage & cluster bootstrap CIs</span>
        </div>
      </div>

      {/* Main Profile Header */}
      {role === 'batter' && currentBatter && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Player Info & Radar */}
          <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="w-8 h-8 rounded-lg bg-[#00FFCC]/20 text-[#00FFCC] flex items-center justify-center font-black text-sm">
                  #{currentBatter.rank}
                </span>
                <Badge variant={currentBatter.reliability_level === 'High' ? 'emerald' : 'amber'}>
                  {currentBatter.reliability_level} Reliability
                </Badge>
              </div>

              <h2 className="text-2xl font-black text-white">
                {currentBatter.player_name}
              </h2>
              <div className="text-xs text-[#8B949E] mt-0.5">
                {currentBatter.batter_classification || 'Elite Under Pressure'}
              </div>

              {/* Main Score Callout */}
              <div className="mt-4 p-4 rounded-xl bg-[#0E1117] border border-[#21262D]">
                <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
                  Final Batter Pressure Rating (FBPR)
                </div>
                <div className="flex items-baseline space-x-3 mt-1">
                  <span className="text-3xl font-black text-[#00FFCC] font-mono">
                    {currentBatter.final_fbpr.toFixed(2)}
                  </span>
                  <span className="text-xs text-[#8B949E] font-mono">
                    95% CI: [{currentBatter.ci_lower_fbpr.toFixed(1)}, {currentBatter.ci_upper_fbpr.toFixed(1)}]
                  </span>
                </div>
              </div>
            </div>

            {/* 5-Axis Spider Radar Chart */}
            <div className="mt-4 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="75%">
                  <PolarGrid stroke="#30363D" />
                  <PolarAngleAxis dataKey="subject" stroke="#8B949E" tick={{ fill: '#8B949E', fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#30363D" tick={false} />
                  <Radar
                    name={currentBatter.player_name}
                    dataKey="value"
                    stroke="#00FFCC"
                    fill="#00FFCC"
                    fillOpacity={0.3}
                  />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload || !payload.length) return null;
                      const d = payload[0].payload;
                      return (
                        <div className="bg-[#1C2128] border border-[#30363D] p-2 rounded text-xs text-white">
                          <span className="font-semibold text-[#00FFCC]">{d.subject}:</span> {d.value.toFixed(1)} / 100
                        </div>
                      );
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Two Columns: Performance Metrics & Dossier */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quantitative Baseline Comparison */}
            <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
                <Target size={16} className="text-[#00FFCC]" />
                <span>Pressure Execution vs Career Baseline</span>
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Pressure Strike Rate</div>
                  <div className="text-lg font-bold text-white font-mono mt-0.5">
                    {currentBatter.strike_rate.toFixed(1)}
                  </div>
                  <div className="text-[10px] text-[#10B981] mt-1 font-semibold">
                    {currentBatter.strike_rate_difference > 0 ? '+' : ''}
                    {currentBatter.strike_rate_difference.toFixed(1)} vs Base
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Normal Baseline SR</div>
                  <div className="text-lg font-bold text-[#8B949E] font-mono mt-0.5">
                    {currentBatter.overall_strike_rate.toFixed(1)}
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    Shrunk career avg
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">SR Retention Rate</div>
                  <div className="text-lg font-bold text-[#00FFCC] font-mono mt-0.5">
                    {currentBatter.strike_rate_retention.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    {currentBatter.strike_rate_retention >= 100 ? 'Accelerates under pressure' : 'Decelerates'}
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Boundary Runs %</div>
                  <div className="text-lg font-bold text-white font-mono mt-0.5">
                    {currentBatter.boundary_percentage.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    {currentBatter.fours} fours, {currentBatter.sixes} sixes
                  </div>
                </div>
              </div>
            </div>

            {/* Qualitative Analytical Dossier */}
            <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Zap size={16} className="text-[#00FFCC]" />
                <span>Analytical Dossier & Evaluation Summary</span>
              </h3>

              <div className="bg-[#0E1117] p-4 rounded-xl border border-[#21262D] text-xs text-[#C9D1D9] leading-relaxed">
                <strong className="text-white block mb-1">Executive Summary:</strong>
                {currentBatter.ranking_explanation}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#0E1117] p-3.5 rounded-xl border border-[#21262D]">
                  <div className="text-xs font-semibold text-[#10B981] flex items-center space-x-1.5 mb-1.5">
                    <CheckCircle2 size={14} />
                    <span>Validated Strengths</span>
                  </div>
                  <p className="text-xs text-[#8B949E] leading-relaxed">
                    {currentBatter.key_strengths}
                  </p>
                </div>

                <div className="bg-[#0E1117] p-3.5 rounded-xl border border-[#21262D]">
                  <div className="text-xs font-semibold text-[#F59E0B] flex items-center space-x-1.5 mb-1.5">
                    <AlertTriangle size={14} />
                    <span>Analytical Limitations</span>
                  </div>
                  <p className="text-xs text-[#8B949E] leading-relaxed">
                    {currentBatter.ranking_limitations || 'Sample variance across distinct innings contexts.'}
                  </p>
                </div>
              </div>

              <div className="text-xs text-[#8B949E] flex items-center justify-between pt-2 border-t border-[#21262D]">
                <span>Exposure: <strong className="text-white">{currentBatter.pressure_exposure}</strong></span>
                <span>Matches: <strong className="text-white">{currentBatter.matches_count}</strong></span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bowler Profile Header */}
      {role === 'bowler' && currentBowler && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Player Info & Radar */}
          <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="w-8 h-8 rounded-lg bg-[#38BDF8]/20 text-[#38BDF8] flex items-center justify-center font-black text-sm">
                  #{currentBowler.rank}
                </span>
                <Badge variant={currentBowler.reliability_level === 'High' ? 'emerald' : 'amber'}>
                  {currentBowler.reliability_level} Reliability
                </Badge>
              </div>

              <h2 className="text-2xl font-black text-white">
                {currentBowler.player_name}
              </h2>
              <div className="text-xs text-[#8B949E] mt-0.5">
                {currentBowler.primary_bowling_style || 'Pace'} • {currentBowler.bowling_role || 'Multi-Phase Bowler'}
              </div>

              {/* Main Score Callout */}
              <div className="mt-4 p-4 rounded-xl bg-[#0E1117] border border-[#21262D]">
                <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
                  Final Bowler Pressure Rating (FBOR)
                </div>
                <div className="flex items-baseline space-x-3 mt-1">
                  <span className="text-3xl font-black text-[#38BDF8] font-mono">
                    {currentBowler.final_fbor.toFixed(2)}
                  </span>
                  <span className="text-xs text-[#8B949E] font-mono">
                    95% CI: [{currentBowler.ci_lower_fbor.toFixed(1)}, {currentBowler.ci_upper_fbor.toFixed(1)}]
                  </span>
                </div>
              </div>
            </div>

            {/* 5-Axis Spider Radar Chart */}
            <div className="mt-4 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="75%">
                  <PolarGrid stroke="#30363D" />
                  <PolarAngleAxis dataKey="subject" stroke="#8B949E" tick={{ fill: '#8B949E', fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#30363D" tick={false} />
                  <Radar
                    name={currentBowler.player_name}
                    dataKey="value"
                    stroke="#38BDF8"
                    fill="#38BDF8"
                    fillOpacity={0.3}
                  />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload || !payload.length) return null;
                      const d = payload[0].payload;
                      return (
                        <div className="bg-[#1C2128] border border-[#30363D] p-2 rounded text-xs text-white">
                          <span className="font-semibold text-[#38BDF8]">{d.subject}:</span> {d.value.toFixed(1)} / 100
                        </div>
                      );
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Two Columns: Performance Metrics & Dossier */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quantitative Baseline Comparison */}
            <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
                <Target size={16} className="text-[#38BDF8]" />
                <span>Pressure Execution vs Career Baseline</span>
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Pressure Economy</div>
                  <div className="text-lg font-bold text-white font-mono mt-0.5">
                    {currentBowler.economy_rate.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-[#10B981] mt-1 font-semibold">
                    {currentBowler.economy_difference <= 0 ? '' : '+'}
                    {currentBowler.economy_difference.toFixed(2)} vs Base
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Normal Baseline Econ</div>
                  <div className="text-lg font-bold text-[#8B949E] font-mono mt-0.5">
                    {currentBowler.overall_economy_rate.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    Career baseline
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">HP Wickets / Overs</div>
                  <div className="text-lg font-bold text-[#38BDF8] font-mono mt-0.5">
                    {currentBowler.wickets_credited} / {(currentBowler.legal_balls_bowled / 6).toFixed(1)} ov
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    {currentBowler.innings_count} innings bowled
                  </div>
                </div>

                <div className="bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
                  <div className="text-[10px] text-[#8B949E]">Dot Ball Control</div>
                  <div className="text-lg font-bold text-[#10B981] font-mono mt-0.5">
                    {currentBowler.dot_ball_percentage.toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-[#8B949E] mt-1">
                    {currentBowler.dot_balls} dot deliveries
                  </div>
                </div>
              </div>
            </div>

            {/* Qualitative Analytical Dossier */}
            <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Zap size={16} className="text-[#38BDF8]" />
                <span>Analytical Dossier & Evaluation Summary</span>
              </h3>

              <div className="bg-[#0E1117] p-4 rounded-xl border border-[#21262D] text-xs text-[#C9D1D9] leading-relaxed">
                <strong className="text-white block mb-1">Executive Summary:</strong>
                {currentBowler.ranking_explanation}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#0E1117] p-3.5 rounded-xl border border-[#21262D]">
                  <div className="text-xs font-semibold text-[#10B981] flex items-center space-x-1.5 mb-1.5">
                    <CheckCircle2 size={14} />
                    <span>Validated Strengths</span>
                  </div>
                  <p className="text-xs text-[#8B949E] leading-relaxed">
                    {currentBowler.key_strengths}
                  </p>
                </div>

                <div className="bg-[#0E1117] p-3.5 rounded-xl border border-[#21262D]">
                  <div className="text-xs font-semibold text-[#F59E0B] flex items-center space-x-1.5 mb-1.5">
                    <AlertTriangle size={14} />
                    <span>Analytical Limitations</span>
                  </div>
                  <p className="text-xs text-[#8B949E] leading-relaxed">
                    {currentBowler.ranking_limitations || 'Spell-to-spell economy variability across distinct match situations.'}
                  </p>
                </div>
              </div>

              <div className="text-xs text-[#8B949E] flex items-center justify-between pt-2 border-t border-[#21262D]">
                <span>Exposure: <strong className="text-white">{currentBowler.pressure_exposure}</strong></span>
                <span>Matches: <strong className="text-white">{currentBowler.matches_count}</strong></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
