import React, { useState, useMemo } from 'react';
import {
  ShieldCheck,
  Search,
  Download,
  Filter,
  Info,
  ChevronDown,
  ExternalLink
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import bowlersData from '../data/bowlers.json';
import { Bowler } from '../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ErrorBar
} from 'recharts';

interface BowlerRankingsViewProps {
  onNavigate: (page: PageId) => void;
  onSelectPlayer?: (playerId: string) => void;
}

export const BowlerRankingsView: React.FC<BowlerRankingsViewProps> = ({
  onNavigate,
  onSelectPlayer
}) => {
  const allBowlers = bowlersData as Bowler[];
  const [viewMode, setViewMode] = useState<'top10' | 'all'>('top10');
  const [searchTerm, setSearchTerm] = useState('');
  const [minBalls, setMinBalls] = useState<number>(120);
  const [styleFilter, setStyleFilter] = useState<'all' | 'Pace' | 'Spin'>('all');
  const [selectedPlayer, setSelectedPlayer] = useState<Bowler | null>(allBowlers[0] || null);

  const filteredBowlers = useMemo(() => {
    return allBowlers.filter((bw) => {
      const matchesSearch = bw.player_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesBalls = (bw.legal_balls_bowled || 0) >= minBalls;
      const matchesStyle =
        styleFilter === 'all' ||
        (bw.primary_bowling_style &&
          bw.primary_bowling_style.toLowerCase().includes(styleFilter.toLowerCase()));

      if (viewMode === 'top10') {
        return bw.rank <= 10 && matchesSearch && matchesStyle;
      }
      return matchesSearch && matchesBalls && matchesStyle;
    });
  }, [allBowlers, viewMode, searchTerm, minBalls, styleFilter]);

  // Chart data preparation with error bounds
  const chartData = useMemo(() => {
    const list = filteredBowlers.slice(0, 15);
    return list.map((bw) => {
      const errPlus = Math.max(0, bw.ci_upper_fbor - bw.final_fbor);
      const errMinus = Math.max(0, bw.final_fbor - bw.ci_lower_fbor);
      return {
        name: bw.player_name,
        rank: bw.rank,
        fbor: bw.final_fbor,
        error: [errMinus, errPlus],
        ciRange: `[${bw.ci_lower_fbor.toFixed(1)}, ${bw.ci_upper_fbor.toFixed(1)}]`,
        raw: bw
      };
    });
  }, [filteredBowlers]);

  const handleExportCSV = () => {
    const headers = [
      'Rank',
      'Player Name',
      'Final FBOR',
      'CI Lower (95%)',
      'CI Upper (95%)',
      'HP Wickets',
      'HP Legal Balls',
      'HP Overs',
      'HP Economy Rate',
      'Baseline Economy Rate',
      'Economy Difference',
      'Dot Ball Pct',
      'Bowling Role',
      'Bowling Style',
      'Reliability',
      'Ranking Explanation'
    ];
    const rows = filteredBowlers.map((bw) => [
      bw.rank,
      `"${bw.player_name}"`,
      bw.final_fbor.toFixed(2),
      bw.ci_lower_fbor.toFixed(2),
      bw.ci_upper_fbor.toFixed(2),
      bw.wickets_credited,
      bw.legal_balls_bowled,
      (bw.legal_balls_bowled / 6).toFixed(1),
      bw.economy_rate.toFixed(2),
      bw.overall_economy_rate.toFixed(2),
      bw.economy_difference.toFixed(2),
      bw.dot_ball_percentage.toFixed(1),
      `"${bw.bowling_role || 'General'}"`,
      bw.primary_bowling_style || 'Pace',
      bw.reliability_level,
      `"${(bw.ranking_explanation || '').replace(/"/g, '""')}"`
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute(
      'download',
      `PressureIQ_Top_Bowlers_${viewMode === 'top10' ? 'Top10' : 'All'}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="blue">Official Evaluation</Badge>
            <span className="text-xs text-[#8B949E] font-mono">232 Eligible Bowlers</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1 flex items-center space-x-3">
            <span>Bowling Clutch Leaderboard</span>
            <span className="text-sm px-2.5 py-0.5 rounded-md bg-[#38BDF8]/10 text-[#38BDF8] font-mono font-semibold">
              FBOR
            </span>
          </h1>
          <p className="text-xs text-[#8B949E] mt-1 max-w-2xl">
            Ranked by Final Bowler Pressure Rating (FBOR), combining run restriction (35%), clutch wickets (30%), consistency (20%), and phase leverage (15%) with empirical Bayes shrinkage.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <div className="inline-flex rounded-xl p-1 bg-[#161B22] border border-[#30363D]">
            <button
              onClick={() => setViewMode('top10')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                viewMode === 'top10'
                  ? 'bg-[#38BDF8] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              Top 10 Official
            </button>
            <button
              onClick={() => setViewMode('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                viewMode === 'all'
                  ? 'bg-[#38BDF8] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              All Eligible (232)
            </button>
          </div>

          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#161B22] border border-[#30363D] hover:border-[#38BDF8]/40 text-xs font-semibold text-[#F0F6FC] transition"
          >
            <Download size={14} className="text-[#38BDF8]" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-64">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8B949E]" />
          <input
            type="text"
            placeholder="Search bowler by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0E1117] border border-[#30363D] rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-[#8B949E] focus:outline-none focus:border-[#38BDF8]"
          />
        </div>

        {/* Style Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-[#8B949E]">Style:</span>
          {(['all', 'Pace', 'Spin'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStyleFilter(st)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition ${
                styleFilter === st
                  ? 'bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/30'
                  : 'text-[#8B949E] hover:text-white bg-[#0E1117]'
              }`}
            >
              {st === 'all' ? 'All Styles' : st}
            </button>
          ))}
        </div>

        {viewMode === 'all' && (
          <div className="flex items-center space-x-3 w-full md:w-auto">
            <span className="text-xs text-[#8B949E] whitespace-nowrap">
              Min HP Deliveries: <strong className="text-white font-mono">{minBalls}</strong>
            </span>
            <input
              type="range"
              min="120"
              max="500"
              step="30"
              value={minBalls}
              onChange={(e) => setMinBalls(Number(e.target.value))}
              className="w-32 accent-[#38BDF8]"
            />
          </div>
        )}

        <div className="text-xs text-[#8B949E] font-mono">
          Showing <span className="text-white font-bold">{filteredBowlers.length}</span> qualified bowlers
        </div>
      </div>

      {/* Interactive Bar Chart with Confidence Intervals */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-[#F0F6FC]">
              FBOR Score Distribution with 95% Bootstrap Confidence Intervals
            </h3>
            <p className="text-xs text-[#8B949E]">
              Error bars represent 95% confidence bounds derived from 1,000 match-level cluster resamples.
            </p>
          </div>
          <Badge variant="blue">95% CI Whisker Overlay</Badge>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
            >
              <XAxis
                type="number"
                domain={[30, 65]}
                stroke="#484F58"
                tick={{ fill: '#8B949E', fontSize: 11 }}
              />
              <YAxis
                dataKey="name"
                type="category"
                stroke="#484F58"
                tick={{ fill: '#F0F6FC', fontSize: 12, fontWeight: 500 }}
                width={120}
              />
              <Tooltip
                content={({ payload }) => {
                  if (!payload || !payload.length) return null;
                  const item = payload[0].payload;
                  const bw = item.raw as Bowler;
                  return (
                    <div className="bg-[#1C2128] border border-[#30363D] p-3 rounded-xl shadow-xl text-xs space-y-1">
                      <div className="font-bold text-white text-sm">
                        #{bw.rank} {bw.player_name}
                      </div>
                      <div className="text-[#38BDF8] font-mono font-bold">
                        FBOR: {bw.final_fbor.toFixed(2)} (95% CI: [{bw.ci_lower_fbor.toFixed(1)}, {bw.ci_upper_fbor.toFixed(1)}])
                      </div>
                      <div className="text-[#8B949E]">
                        HP Wickets: <strong className="text-white">{bw.wickets_credited}</strong> ({bw.legal_balls_bowled} balls)
                      </div>
                      <div className="text-[#8B949E]">
                        Pressure Econ: <strong className="text-white">{bw.economy_rate.toFixed(2)}</strong> vs Normal {bw.overall_economy_rate.toFixed(2)}
                      </div>
                      <div className="text-[#8B949E] text-[10px] mt-1 pt-1 border-t border-[#30363D]">
                        Click row below to view full deep-dive dossier
                      </div>
                    </div>
                  );
                }}
              />
              <Bar dataKey="fbor" radius={[0, 6, 6, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.rank === 1 ? '#38BDF8' : entry.rank <= 3 ? '#00FFCC' : '#818CF8'}
                  />
                ))}
                <ErrorBar dataKey="error" width={4} strokeWidth={2} stroke="#F0F6FC" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Selected Bowler Deep-Dive Card */}
      {selectedPlayer && (
        <div className="bg-gradient-to-r from-[#161B22] to-[#1C2128] border border-[#38BDF8]/30 rounded-2xl p-6 shadow-lg shadow-[#38BDF8]/5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div className="flex items-center space-x-3">
              <span className="w-9 h-9 rounded-xl bg-[#38BDF8]/20 text-[#38BDF8] flex items-center justify-center font-black text-sm">
                #{selectedPlayer.rank}
              </span>
              <div>
                <h3 className="text-xl font-black text-[#F0F6FC]">
                  {selectedPlayer.player_name}
                </h3>
                <div className="flex items-center space-x-2 text-xs text-[#8B949E]">
                  <span>{selectedPlayer.primary_bowling_style || 'Pace'}</span>
                  <span>•</span>
                  <span>{selectedPlayer.bowling_role || 'Multi-Phase Bowler'}</span>
                  <span>•</span>
                  <span>{selectedPlayer.reliability_summary}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-black text-[#38BDF8] font-mono">
                  {selectedPlayer.final_fbor.toFixed(2)}
                </div>
                <div className="text-[10px] text-[#8B949E]">FBOR RATING</div>
              </div>
              <button
                onClick={() => {
                  if (onSelectPlayer) onSelectPlayer(selectedPlayer.player_id);
                  onNavigate('player-analysis');
                }}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/30 hover:bg-[#38BDF8]/20 text-xs font-bold transition"
              >
                <span>Full Dossier</span>
                <ExternalLink size={14} />
              </button>
            </div>
          </div>

          <p className="text-xs text-[#C9D1D9] bg-[#0E1117] p-3.5 rounded-xl border border-[#21262D] mb-4">
            {selectedPlayer.ranking_explanation}
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">HP Wickets / Overs</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.wickets_credited} / {(selectedPlayer.legal_balls_bowled / 6).toFixed(1)} ov
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Pressure Econ</div>
              <div className="text-sm font-bold text-[#38BDF8] font-mono">
                {selectedPlayer.economy_rate.toFixed(2)}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Baseline Econ</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.overall_economy_rate.toFixed(2)}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Dot Ball %</div>
              <div className="text-sm font-bold text-[#10B981] font-mono">
                {selectedPlayer.dot_ball_percentage.toFixed(1)}%
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Bowling Avg</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.bowling_average.toFixed(1)}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">95% CI Width</div>
              <div className="text-sm font-bold text-[#00FFCC] font-mono">
                ±{(selectedPlayer.ci_width_fbor / 2).toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Leaderboard Table */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D] flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#F0F6FC]">
            Official Ranking Table ({filteredBowlers.length} qualified)
          </h3>
          <span className="text-xs text-[#8B949E]">Click any row to inspect bowler</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] uppercase font-mono tracking-wider">
              <tr>
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Player</th>
                <th className="py-3 px-4 text-right">FBOR</th>
                <th className="py-3 px-4 text-center">95% CI</th>
                <th className="py-3 px-4 text-right">HP Wkts</th>
                <th className="py-3 px-4 text-right">HP Overs</th>
                <th className="py-3 px-4 text-right">HP Econ</th>
                <th className="py-3 px-4 text-right">Base Econ</th>
                <th className="py-3 px-4 text-right">Dot %</th>
                <th className="py-3 px-4 text-center">Style</th>
                <th className="py-3 px-4 text-center">Reliability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {filteredBowlers.map((bw) => {
                const isSelected = selectedPlayer?.player_id === bw.player_id;
                return (
                  <tr
                    key={bw.player_id}
                    onClick={() => setSelectedPlayer(bw)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-[#38BDF8]/10 text-white font-medium'
                        : 'hover:bg-[#1C2128] text-[#C9D1D9]'
                    }`}
                  >
                    <td className="py-3 px-4 font-mono font-bold text-[#8B949E]">
                      #{bw.rank}
                    </td>
                    <td className="py-3 px-4 font-medium text-white flex items-center space-x-2">
                      <span>{bw.player_name}</span>
                      {bw.rank <= 3 && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#38BDF8]/20 text-[#38BDF8]">
                          PODIUM
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-[#38BDF8]">
                      {bw.final_fbor.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center font-mono text-[#8B949E] text-[11px]">
                      [{bw.ci_lower_fbor.toFixed(1)}, {bw.ci_upper_fbor.toFixed(1)}]
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-white">
                      {bw.wickets_credited}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#8B949E]">
                      {(bw.legal_balls_bowled / 6).toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-white">
                      {bw.economy_rate.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#8B949E]">
                      {bw.overall_economy_rate.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#10B981]">
                      {bw.dot_ball_percentage.toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-[#21262D] text-[#C9D1D9]">
                        {bw.primary_bowling_style || 'Pace'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge
                        variant={
                          bw.reliability_level === 'High'
                            ? 'emerald'
                            : bw.reliability_level === 'Moderate'
                            ? 'amber'
                            : 'gray'
                        }
                        size="sm"
                      >
                        {bw.reliability_level}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
