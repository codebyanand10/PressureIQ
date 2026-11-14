import React, { useState, useMemo } from 'react';
import {
  Award,
  Search,
  Download,
  Filter,
  Info,
  ChevronDown,
  TrendingUp,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import battersData from '../data/batters.json';
import { Batter } from '../types';
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

interface BatterRankingsViewProps {
  onNavigate: (page: PageId) => void;
  onSelectPlayer?: (playerId: string) => void;
}

export const BatterRankingsView: React.FC<BatterRankingsViewProps> = ({
  onNavigate,
  onSelectPlayer
}) => {
  const allBatters = battersData as Batter[];
  const [viewMode, setViewMode] = useState<'top10' | 'all'>('top10');
  const [searchTerm, setSearchTerm] = useState('');
  const [minBalls, setMinBalls] = useState<number>(100);
  const [selectedPlayer, setSelectedPlayer] = useState<Batter | null>(allBatters[0] || null);

  const filteredBatters = useMemo(() => {
    return allBatters.filter((b) => {
      const matchesSearch = b.player_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesBalls = (b.balls_faced || 0) >= minBalls;
      if (viewMode === 'top10') {
        return b.rank <= 10 && matchesSearch;
      }
      return matchesSearch && matchesBalls;
    });
  }, [allBatters, viewMode, searchTerm, minBalls]);

  // Chart data preparation with error bounds
  const chartData = useMemo(() => {
    const list = filteredBatters.slice(0, 15);
    return list.map((b) => {
      const errPlus = Math.max(0, b.ci_upper_fbpr - b.final_fbpr);
      const errMinus = Math.max(0, b.final_fbpr - b.ci_lower_fbpr);
      return {
        name: b.player_name,
        rank: b.rank,
        fbpr: b.final_fbpr,
        error: [errMinus, errPlus],
        ciRange: `[${b.ci_lower_fbpr.toFixed(1)}, ${b.ci_upper_fbpr.toFixed(1)}]`,
        raw: b
      };
    });
  }, [filteredBatters]);

  const handleExportCSV = () => {
    const headers = [
      'Rank',
      'Player Name',
      'Final FBPR',
      'CI Lower (95%)',
      'CI Upper (95%)',
      'HP Runs',
      'HP Balls Faced',
      'HP Strike Rate',
      'Baseline Strike Rate',
      'SR Difference',
      'Boundary Pct',
      'Reliability',
      'Ranking Explanation'
    ];
    const rows = filteredBatters.map((b) => [
      b.rank,
      `"${b.player_name}"`,
      b.final_fbpr.toFixed(2),
      b.ci_lower_fbpr.toFixed(2),
      b.ci_upper_fbpr.toFixed(2),
      b.total_runs,
      b.balls_faced,
      b.strike_rate.toFixed(1),
      b.overall_strike_rate.toFixed(1),
      b.strike_rate_difference.toFixed(1),
      b.boundary_percentage.toFixed(1),
      b.reliability_level,
      `"${(b.ranking_explanation || '').replace(/"/g, '""')}"`
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute(
      'download',
      `PressureIQ_Top_Batters_${viewMode === 'top10' ? 'Top10' : 'All'}.csv`
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
            <Badge variant="teal">Official Evaluation</Badge>
            <span className="text-xs text-[#8B949E] font-mono">170 Eligible Batters</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1 flex items-center space-x-3">
            <span>Batting Clutch Leaderboard</span>
            <span className="text-sm px-2.5 py-0.5 rounded-md bg-[#00FFCC]/10 text-[#00FFCC] font-mono font-semibold">
              FBPR
            </span>
          </h1>
          <p className="text-xs text-[#8B949E] mt-1 max-w-2xl">
            Ranked by Final Batter Pressure Rating (FBPR), integrating resilience (35%), absolute scoring (30%), consistency (20%), and context leverage (15%) with empirical Bayes shrinkage.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <div className="inline-flex rounded-xl p-1 bg-[#161B22] border border-[#30363D]">
            <button
              onClick={() => setViewMode('top10')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                viewMode === 'top10'
                  ? 'bg-[#00FFCC] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              Top 10 Official
            </button>
            <button
              onClick={() => setViewMode('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                viewMode === 'all'
                  ? 'bg-[#00FFCC] text-[#0E1117] shadow-sm'
                  : 'text-[#8B949E] hover:text-white'
              }`}
            >
              All Eligible (170)
            </button>
          </div>

          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#161B22] border border-[#30363D] hover:border-[#00FFCC]/40 text-xs font-semibold text-[#F0F6FC] transition"
          >
            <Download size={14} className="text-[#00FFCC]" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-72">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8B949E]" />
          <input
            type="text"
            placeholder="Search batter by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0E1117] border border-[#30363D] rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-[#8B949E] focus:outline-none focus:border-[#00FFCC]"
          />
        </div>

        {viewMode === 'all' && (
          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <span className="text-xs text-[#8B949E] whitespace-nowrap">
              Min HP Balls Faced: <strong className="text-white font-mono">{minBalls}</strong>
            </span>
            <input
              type="range"
              min="100"
              max="400"
              step="20"
              value={minBalls}
              onChange={(e) => setMinBalls(Number(e.target.value))}
              className="w-32 accent-[#00FFCC]"
            />
          </div>
        )}

        <div className="text-xs text-[#8B949E] font-mono">
          Showing <span className="text-white font-bold">{filteredBatters.length}</span> qualified batters
        </div>
      </div>

      {/* Interactive Bar Chart with Confidence Intervals */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-[#F0F6FC]">
              FBPR Score Distribution with 95% Bootstrap Confidence Intervals
            </h3>
            <p className="text-xs text-[#8B949E]">
              Error bars represent 95% confidence bounds derived from 1,000 match-level cluster resamples.
            </p>
          </div>
          <Badge variant="teal">95% CI Whisker Overlay</Badge>
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
                domain={[40, 100]}
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
                  const b = item.raw as Batter;
                  return (
                    <div className="bg-[#1C2128] border border-[#30363D] p-3 rounded-xl shadow-xl text-xs space-y-1">
                      <div className="font-bold text-white text-sm">
                        #{b.rank} {b.player_name}
                      </div>
                      <div className="text-[#00FFCC] font-mono font-bold">
                        FBPR: {b.final_fbpr.toFixed(2)} (95% CI: [{b.ci_lower_fbpr.toFixed(1)}, {b.ci_upper_fbpr.toFixed(1)}])
                      </div>
                      <div className="text-[#8B949E]">
                        HP Runs: <strong className="text-white">{b.total_runs}</strong> ({b.balls_faced} balls)
                      </div>
                      <div className="text-[#8B949E]">
                        Pressure SR: <strong className="text-white">{b.strike_rate.toFixed(1)}</strong> vs Normal {b.overall_strike_rate.toFixed(1)}
                      </div>
                      <div className="text-[#8B949E] text-[10px] mt-1 pt-1 border-t border-[#30363D]">
                        Click row below to view full deep-dive dossier
                      </div>
                    </div>
                  );
                }}
              />
              <Bar dataKey="fbpr" radius={[0, 6, 6, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.rank === 1 ? '#00FFCC' : entry.rank <= 3 ? '#38BDF8' : '#818CF8'}
                  />
                ))}
                <ErrorBar dataKey="error" width={4} strokeWidth={2} stroke="#F0F6FC" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Selected Batter Deep-Dive Card */}
      {selectedPlayer && (
        <div className="bg-gradient-to-r from-[#161B22] to-[#1C2128] border border-[#00FFCC]/30 rounded-2xl p-6 shadow-lg shadow-[#00FFCC]/5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div className="flex items-center space-x-3">
              <span className="w-9 h-9 rounded-xl bg-[#00FFCC]/20 text-[#00FFCC] flex items-center justify-center font-black text-sm">
                #{selectedPlayer.rank}
              </span>
              <div>
                <h3 className="text-xl font-black text-[#F0F6FC]">
                  {selectedPlayer.player_name}
                </h3>
                <div className="flex items-center space-x-2 text-xs text-[#8B949E]">
                  <span>{selectedPlayer.batter_classification || 'Elite Under Pressure'}</span>
                  <span>•</span>
                  <span>{selectedPlayer.reliability_summary}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-black text-[#00FFCC] font-mono">
                  {selectedPlayer.final_fbpr.toFixed(2)}
                </div>
                <div className="text-[10px] text-[#8B949E]">FBPR RATING</div>
              </div>
              <button
                onClick={() => {
                  if (onSelectPlayer) onSelectPlayer(selectedPlayer.player_id);
                  onNavigate('player-analysis');
                }}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#00FFCC]/10 text-[#00FFCC] border border-[#00FFCC]/30 hover:bg-[#00FFCC]/20 text-xs font-bold transition"
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
              <div className="text-[10px] text-[#8B949E]">HP Runs / Balls</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.total_runs} / {selectedPlayer.balls_faced}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Pressure SR</div>
              <div className="text-sm font-bold text-[#00FFCC] font-mono">
                {selectedPlayer.strike_rate.toFixed(1)}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Baseline SR</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.overall_strike_rate.toFixed(1)}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">SR Retention</div>
              <div className="text-sm font-bold text-[#10B981] font-mono">
                {selectedPlayer.strike_rate_retention.toFixed(1)}%
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">Boundary Runs %</div>
              <div className="text-sm font-bold text-white font-mono">
                {selectedPlayer.boundary_percentage.toFixed(1)}%
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0E1117] border border-[#21262D]">
              <div className="text-[10px] text-[#8B949E]">95% CI Width</div>
              <div className="text-sm font-bold text-[#38BDF8] font-mono">
                ±{(selectedPlayer.ci_width_fbpr / 2).toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Leaderboard Table */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D] flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#F0F6FC]">
            Official Ranking Table ({filteredBatters.length} qualified)
          </h3>
          <span className="text-xs text-[#8B949E]">Click any row to inspect player</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] uppercase font-mono tracking-wider">
              <tr>
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Player</th>
                <th className="py-3 px-4 text-right">FBPR</th>
                <th className="py-3 px-4 text-center">95% CI</th>
                <th className="py-3 px-4 text-right">HP Runs</th>
                <th className="py-3 px-4 text-right">HP Balls</th>
                <th className="py-3 px-4 text-right">HP SR</th>
                <th className="py-3 px-4 text-right">Base SR</th>
                <th className="py-3 px-4 text-right">SR Diff</th>
                <th className="py-3 px-4 text-center">Reliability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {filteredBatters.map((b) => {
                const isSelected = selectedPlayer?.player_id === b.player_id;
                return (
                  <tr
                    key={b.player_id}
                    onClick={() => setSelectedPlayer(b)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-[#00FFCC]/10 text-white font-medium'
                        : 'hover:bg-[#1C2128] text-[#C9D1D9]'
                    }`}
                  >
                    <td className="py-3 px-4 font-mono font-bold text-[#8B949E]">
                      #{b.rank}
                    </td>
                    <td className="py-3 px-4 font-medium text-white flex items-center space-x-2">
                      <span>{b.player_name}</span>
                      {b.rank <= 3 && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#00FFCC]/20 text-[#00FFCC]">
                          PODIUM
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-[#00FFCC]">
                      {b.final_fbpr.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center font-mono text-[#8B949E] text-[11px]">
                      [{b.ci_lower_fbpr.toFixed(1)}, {b.ci_upper_fbpr.toFixed(1)}]
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-white">
                      {b.total_runs}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#8B949E]">
                      {b.balls_faced}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-white">
                      {b.strike_rate.toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-[#8B949E]">
                      {b.overall_strike_rate.toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-right font-mono">
                      <span
                        className={
                          b.strike_rate_difference >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'
                        }
                      >
                        {b.strike_rate_difference > 0 ? '+' : ''}
                        {b.strike_rate_difference.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge
                        variant={
                          b.reliability_level === 'High'
                            ? 'emerald'
                            : b.reliability_level === 'Moderate'
                            ? 'amber'
                            : 'gray'
                        }
                        size="sm"
                      >
                        {b.reliability_level}
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
