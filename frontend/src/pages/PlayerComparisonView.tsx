import React, { useState, useMemo } from 'react';
import {
  Users,
  Award,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  XCircle
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
  Legend,
  Tooltip
} from 'recharts';

interface PlayerComparisonViewProps {
  onNavigate: (page: PageId) => void;
}

export const PlayerComparisonView: React.FC<PlayerComparisonViewProps> = ({ onNavigate }) => {
  const allBatters = battersData as Batter[];
  const allBowlers = bowlersData as Bowler[];

  const [role, setRole] = useState<'batter' | 'bowler'>('batter');
  const [playerAId, setPlayerAId] = useState<string>(allBatters[0]?.player_id || '4708');
  const [playerBId, setPlayerBId] = useState<string>(allBatters[1]?.player_id || '796');

  const playerA = useMemo(() => {
    if (role === 'batter') {
      return allBatters.find((b) => b.player_id === playerAId) || allBatters[0];
    }
    return allBowlers.find((bw) => bw.player_id === playerAId) || allBowlers[0];
  }, [role, playerAId, allBatters, allBowlers]);

  const playerB = useMemo(() => {
    if (role === 'batter') {
      return allBatters.find((b) => b.player_id === playerBId) || allBatters[1];
    }
    return allBowlers.find((bw) => bw.player_id === playerBId) || allBowlers[1];
  }, [role, playerBId, allBatters, allBowlers]);

  // Dual Radar comparison data
  const comparisonRadarData = useMemo(() => {
    if (role === 'batter' && playerA && playerB) {
      const bA = playerA as Batter;
      const bB = playerB as Batter;
      return [
        {
          subject: 'Resilience (BPPI)',
          playerA: bA.score_batting_resilience || 70,
          playerB: bB.score_batting_resilience || 70,
        },
        {
          subject: 'Absolute Power',
          playerA: bA.score_batting_absolute || 80,
          playerB: bB.score_batting_absolute || 80,
        },
        {
          subject: 'Consistency',
          playerA: bA.score_batting_consistency || 65,
          playerB: bB.score_batting_consistency || 65,
        },
        {
          subject: 'Context Clutch',
          playerA: bA.score_batting_context || 70,
          playerB: bB.score_batting_context || 70,
        },
        {
          subject: 'SR Retention',
          playerA: Math.min(100, (bA.strike_rate_retention / 2) || 70),
          playerB: Math.min(100, (bB.strike_rate_retention / 2) || 70),
        },
      ];
    } else if (playerA && playerB) {
      const bwA = playerA as Bowler;
      const bwB = playerB as Bowler;
      return [
        {
          subject: 'Resilience (BPPI-B)',
          playerA: bwA.score_bowling_resilience || 70,
          playerB: bwB.score_bowling_resilience || 70,
        },
        {
          subject: 'Run Restriction',
          playerA: bwA.score_bowling_absolute || 75,
          playerB: bwB.score_bowling_absolute || 75,
        },
        {
          subject: 'Consistency',
          playerA: bwA.score_bowling_consistency || 60,
          playerB: bwB.score_bowling_consistency || 60,
        },
        {
          subject: 'Phase Leverage',
          playerA: bwA.score_bowling_context || 65,
          playerB: bwB.score_bowling_context || 65,
        },
        {
          subject: 'Dot Pressure',
          playerA: Math.min(100, bwA.dot_ball_percentage * 1.5 || 60),
          playerB: Math.min(100, bwB.dot_ball_percentage * 1.5 || 60),
        },
      ];
    }
    return [];
  }, [role, playerA, playerB]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Controls */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-white flex items-center space-x-2">
            <Users size={20} className="text-[#00FFCC]" />
            <span>Head-to-Head Clutch Comparison</span>
          </h1>
          <p className="text-xs text-[#8B949E] mt-0.5">
            Direct multi-dimensional audit of pressure execution and statistical separation
          </p>
        </div>

        <div className="inline-flex rounded-xl p-1 bg-[#0E1117] border border-[#21262D]">
          <button
            onClick={() => {
              setRole('batter');
              setPlayerAId(allBatters[0]?.player_id || '');
              setPlayerBId(allBatters[1]?.player_id || '');
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
              role === 'batter'
                ? 'bg-[#00FFCC] text-[#0E1117] shadow-sm'
                : 'text-[#8B949E] hover:text-white'
            }`}
          >
            <Award size={14} />
            <span>Compare Batters</span>
          </button>
          <button
            onClick={() => {
              setRole('bowler');
              setPlayerAId(allBowlers[0]?.player_id || '');
              setPlayerBId(allBowlers[1]?.player_id || '');
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
              role === 'bowler'
                ? 'bg-[#38BDF8] text-[#0E1117] shadow-sm'
                : 'text-[#8B949E] hover:text-white'
            }`}
          >
            <ShieldCheck size={14} />
            <span>Compare Bowlers</span>
          </button>
        </div>
      </div>

      {/* Selectors and Versus Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Player A Card */}
        <div className="bg-[#161B22] border border-[#00FFCC]/40 rounded-2xl p-5 shadow-lg shadow-[#00FFCC]/5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono font-bold text-[#00FFCC] uppercase tracking-wider">
              Player A
            </span>
            <Badge variant="teal">Rank #{playerA?.rank}</Badge>
          </div>
          <select
            value={playerAId}
            onChange={(e) => setPlayerAId(e.target.value)}
            className="w-full bg-[#0E1117] text-white border border-[#30363D] rounded-xl px-4 py-2.5 text-sm font-semibold focus:outline-none focus:border-[#00FFCC]"
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
          <div className="mt-4 flex items-center justify-between bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
            <span className="text-xs text-[#8B949E]">
              {role === 'batter' ? 'FBPR Rating' : 'FBOR Rating'}
            </span>
            <span className="text-xl font-black text-[#00FFCC] font-mono">
              {role === 'batter'
                ? (playerA as Batter)?.final_fbpr.toFixed(2)
                : (playerA as Bowler)?.final_fbor.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Player B Card */}
        <div className="bg-[#161B22] border border-[#38BDF8]/40 rounded-2xl p-5 shadow-lg shadow-[#38BDF8]/5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono font-bold text-[#38BDF8] uppercase tracking-wider">
              Player B
            </span>
            <Badge variant="blue">Rank #{playerB?.rank}</Badge>
          </div>
          <select
            value={playerBId}
            onChange={(e) => setPlayerBId(e.target.value)}
            className="w-full bg-[#0E1117] text-white border border-[#30363D] rounded-xl px-4 py-2.5 text-sm font-semibold focus:outline-none focus:border-[#38BDF8]"
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
          <div className="mt-4 flex items-center justify-between bg-[#0E1117] p-3 rounded-xl border border-[#21262D]">
            <span className="text-xs text-[#8B949E]">
              {role === 'batter' ? 'FBPR Rating' : 'FBOR Rating'}
            </span>
            <span className="text-xl font-black text-[#38BDF8] font-mono">
              {role === 'batter'
                ? (playerB as Batter)?.final_fbpr.toFixed(2)
                : (playerB as Bowler)?.final_fbor.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Dual Radar Chart Overlay & Comparison Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Overlay */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white">
              Multi-Dimensional Attribute Overlay
            </h3>
            <div className="flex items-center space-x-3 text-xs">
              <span className="flex items-center space-x-1 text-[#00FFCC]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#00FFCC]"></span>
                <span>{playerA?.player_name}</span>
              </span>
              <span className="flex items-center space-x-1 text-[#38BDF8]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#38BDF8]"></span>
                <span>{playerB?.player_name}</span>
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={comparisonRadarData} outerRadius="75%">
                <PolarGrid stroke="#30363D" />
                <PolarAngleAxis dataKey="subject" stroke="#8B949E" tick={{ fill: '#8B949E', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#30363D" tick={false} />
                <Radar
                  name={playerA?.player_name}
                  dataKey="playerA"
                  stroke="#00FFCC"
                  fill="#00FFCC"
                  fillOpacity={0.25}
                />
                <Radar
                  name={playerB?.player_name}
                  dataKey="playerB"
                  stroke="#38BDF8"
                  fill="#38BDF8"
                  fillOpacity={0.25}
                />
                <Tooltip
                  content={({ payload }) => {
                    if (!payload || !payload.length) return null;
                    return (
                      <div className="bg-[#1C2128] border border-[#30363D] p-2.5 rounded text-xs space-y-1">
                        <div className="text-white font-semibold">{payload[0]?.payload?.subject}</div>
                        <div className="text-[#00FFCC]">
                          {playerA?.player_name}: {Number(payload[0]?.value).toFixed(1)}
                        </div>
                        <div className="text-[#38BDF8]">
                          {playerB?.player_name}: {Number(payload[1]?.value).toFixed(1)}
                        </div>
                      </div>
                    );
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Delta Table */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">
            Key Metrics Side-by-Side Delta
          </h3>

          <div className="space-y-3">
            {role === 'batter' ? (
              <>
                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">Pressure Strike Rate</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono font-bold text-[#00FFCC]">
                      {(playerA as Batter)?.strike_rate.toFixed(1)}
                    </span>
                    <span className="text-xs font-mono font-bold text-[#38BDF8]">
                      {(playerB as Batter)?.strike_rate.toFixed(1)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">Baseline Career SR</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerA as Batter)?.overall_strike_rate.toFixed(1)}
                    </span>
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerB as Batter)?.overall_strike_rate.toFixed(1)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">SR Difference (Delta)</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono font-bold text-[#10B981]">
                      +{(playerA as Batter)?.strike_rate_difference.toFixed(1)}
                    </span>
                    <span className="text-xs font-mono font-bold text-[#10B981]">
                      +{(playerB as Batter)?.strike_rate_difference.toFixed(1)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">Boundary Runs %</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono text-white">
                      {(playerA as Batter)?.boundary_percentage.toFixed(1)}%
                    </span>
                    <span className="text-xs font-mono text-white">
                      {(playerB as Batter)?.boundary_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">HP Balls Faced</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerA as Batter)?.balls_faced}
                    </span>
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerB as Batter)?.balls_faced}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">95% CI Range</span>
                  <div className="flex items-center space-x-4 text-[11px] font-mono">
                    <span className="text-[#00FFCC]">
                      [{(playerA as Batter)?.ci_lower_fbpr.toFixed(1)}, {(playerA as Batter)?.ci_upper_fbpr.toFixed(1)}]
                    </span>
                    <span className="text-[#38BDF8]">
                      [{(playerB as Batter)?.ci_lower_fbpr.toFixed(1)}, {(playerB as Batter)?.ci_upper_fbpr.toFixed(1)}]
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">Pressure Economy</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono font-bold text-[#00FFCC]">
                      {(playerA as Bowler)?.economy_rate.toFixed(2)}
                    </span>
                    <span className="text-xs font-mono font-bold text-[#38BDF8]">
                      {(playerB as Bowler)?.economy_rate.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">HP Wickets Credited</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono text-white">
                      {(playerA as Bowler)?.wickets_credited}
                    </span>
                    <span className="text-xs font-mono text-white">
                      {(playerB as Bowler)?.wickets_credited}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">Dot Ball Control</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono font-bold text-[#10B981]">
                      {(playerA as Bowler)?.dot_ball_percentage.toFixed(1)}%
                    </span>
                    <span className="text-xs font-mono font-bold text-[#10B981]">
                      {(playerB as Bowler)?.dot_ball_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">HP Legal Balls Bowled</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerA as Bowler)?.legal_balls_bowled}
                    </span>
                    <span className="text-xs font-mono text-[#8B949E]">
                      {(playerB as Bowler)?.legal_balls_bowled}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-[#0E1117] border border-[#21262D]">
                  <span className="text-xs text-[#8B949E]">95% CI Range</span>
                  <div className="flex items-center space-x-4 text-[11px] font-mono">
                    <span className="text-[#00FFCC]">
                      [{(playerA as Bowler)?.ci_lower_fbor.toFixed(1)}, {(playerA as Bowler)?.ci_upper_fbor.toFixed(1)}]
                    </span>
                    <span className="text-[#38BDF8]">
                      [{(playerB as Bowler)?.ci_lower_fbor.toFixed(1)}, {(playerB as Bowler)?.ci_upper_fbor.toFixed(1)}]
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
