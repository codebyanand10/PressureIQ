import React from 'react';
import {
  Activity,
  Flame,
  ShieldCheck,
  Award,
  TrendingUp,
  Zap,
  ArrowRight,
  Database,
  BarChart3,
  Layers
} from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import overviewData from '../data/overview.json';
import battersData from '../data/batters.json';
import bowlersData from '../data/bowlers.json';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

interface OverviewViewProps {
  onNavigate: (page: PageId) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate }) => {
  const telemetry = overviewData.macro_telemetry;
  const highlights = overviewData.clutch_highlights;
  
  // Transform pressure tier distribution for Recharts
  const tierDistributionData = Object.entries(overviewData.pressure_tier_distribution).map(
    ([tier, count]) => ({
      tier,
      count,
      pct: ((count / telemetry.total_deliveries) * 100).toFixed(1),
    })
  );

  const TIER_COLORS: Record<string, string> = {
    'Low Pressure': '#38BDF8',
    'Medium Pressure': '#F59E0B',
    'High Pressure': '#EF4444',
    'Extreme Pressure': '#A855F7',
  };

  const topBatters = (battersData as any[]).slice(0, 5);
  const topBowlers = (bowlersData as any[]).slice(0, 5);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#161B22] via-[#1C2128] to-[#161B22] border border-[#30363D] p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#00FFCC]/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-3xl">
          <div className="flex items-center space-x-2 mb-3">
            <Badge variant="teal">SupeRR Selector Season 2</Badge>
            <Badge variant="blue">Official Submission</Badge>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F0F6FC] tracking-tight">
            Pressure<span className="text-[#00FFCC]">IQ</span> Analytics Engine
          </h1>
          <p className="mt-3 text-[#8B949E] text-base leading-relaxed">
            A physics-grounded, bimodal rating framework quantifying clutch execution across 
            <strong className="text-[#F0F6FC]"> 227,100 balls</strong>, 
            <strong className="text-[#F0F6FC]"> 950 IPL matches</strong>, and 
            <strong className="text-[#F0F6FC]"> 582 evaluated players</strong> using Empirical Bayes shrinkage and 95% bootstrap confidence intervals.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('batter-rankings')}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#00FFCC] text-[#0E1117] font-bold text-sm hover:bg-[#00CC99] transition shadow-lg shadow-[#00FFCC]/20"
            >
              <Award size={16} />
              <span>Explore Top 10 Batters</span>
              <ArrowRight size={14} />
            </button>
            <button
              onClick={() => onNavigate('bowler-rankings')}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#1F242C] text-[#F0F6FC] font-semibold text-sm border border-[#30363D] hover:border-[#00FFCC]/40 transition"
            >
              <ShieldCheck size={16} />
              <span>Explore Top 10 Bowlers</span>
            </button>
            <button
              onClick={() => onNavigate('methodology')}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#161B22] text-[#8B949E] hover:text-[#F0F6FC] text-sm border border-[#21262D] hover:border-[#30363D] transition"
            >
              <span>Methodology & Math</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Telemetry Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Deliveries"
          value={telemetry.total_deliveries.toLocaleString()}
          subValue="100% Cardinality Intact"
          icon={Database}
          variant="blue"
        />
        <StatCard
          label="High-Pressure Balls"
          value={telemetry.high_pressure_deliveries.toLocaleString()}
          subValue={`${telemetry.high_pressure_percentage}% of tournament balls`}
          icon={Flame}
          variant="amber"
        />
        <StatCard
          label="Eligible Batters"
          value={`${telemetry.eligible_batters} / ${telemetry.evaluated_batters}`}
          subValue="≥100 HP balls faced filter"
          icon={Award}
          variant="teal"
        />
        <StatCard
          label="Eligible Bowlers"
          value={`${telemetry.eligible_bowlers} / ${telemetry.evaluated_bowlers}`}
          subValue="≥120 HP legal deliveries filter"
          icon={ShieldCheck}
          variant="emerald"
        />
      </div>

      {/* Clutch Spotlight: #1 Batter & #1 Bowler */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Batter #1 Spotlight */}
        <div className="bg-[#161B22] border border-[#00FFCC]/30 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-[#00FFCC]/5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <span className="w-8 h-8 rounded-lg bg-[#00FFCC]/20 text-[#00FFCC] flex items-center justify-center font-bold text-sm">
                #1
              </span>
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-[#8B949E]">
                  Official #1 Clutch Batter
                </span>
                <h3 className="text-xl font-black text-[#F0F6FC]">
                  {highlights.batting.player_name}
                </h3>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-black text-[#00FFCC] font-mono">
                {highlights.batting.final_fbpr.toFixed(2)}
              </div>
              <div className="text-[10px] text-[#8B949E] uppercase tracking-wider">
                FBPR Score
              </div>
            </div>
          </div>
          <p className="text-xs text-[#8B949E] leading-relaxed mb-4">
            {highlights.batting.explanation}
          </p>
          <div className="grid grid-cols-3 gap-2 bg-[#0E1117] p-3 rounded-xl border border-[#21262D] text-center">
            <div>
              <div className="text-xs text-[#8B949E]">Pressure SR</div>
              <div className="text-base font-bold text-[#F0F6FC] font-mono">
                {highlights.batting.strike_rate.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#8B949E]">HP Balls</div>
              <div className="text-base font-bold text-[#F0F6FC] font-mono">
                {highlights.batting.high_pressure_balls}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#8B949E]">Baseline Diff</div>
              <div className="text-base font-bold text-[#10B981] font-mono">
                +56.7 SR
              </div>
            </div>
          </div>
        </div>

        {/* Bowler #1 Spotlight */}
        <div className="bg-[#161B22] border border-[#38BDF8]/30 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-[#38BDF8]/5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <span className="w-8 h-8 rounded-lg bg-[#38BDF8]/20 text-[#38BDF8] flex items-center justify-center font-bold text-sm">
                #1
              </span>
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-[#8B949E]">
                  Official #1 Clutch Bowler
                </span>
                <h3 className="text-xl font-black text-[#F0F6FC]">
                  {highlights.bowling.player_name}
                </h3>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-black text-[#38BDF8] font-mono">
                {highlights.bowling.final_fbor.toFixed(2)}
              </div>
              <div className="text-[10px] text-[#8B949E] uppercase tracking-wider">
                FBOR Score
              </div>
            </div>
          </div>
          <p className="text-xs text-[#8B949E] leading-relaxed mb-4">
            {highlights.bowling.explanation}
          </p>
          <div className="grid grid-cols-3 gap-2 bg-[#0E1117] p-3 rounded-xl border border-[#21262D] text-center">
            <div>
              <div className="text-xs text-[#8B949E]">Pressure Econ</div>
              <div className="text-base font-bold text-[#F0F6FC] font-mono">
                {highlights.bowling.economy_rate.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#8B949E]">HP Wickets</div>
              <div className="text-base font-bold text-[#F0F6FC] font-mono">
                {highlights.bowling.wickets}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#8B949E]">Dot Ball %</div>
              <div className="text-base font-bold text-[#10B981] font-mono">
                42.1%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Distribution & Quick Leaderboards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pressure Tier Bar Chart */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-[#F0F6FC] flex items-center space-x-2">
              <BarChart3 size={18} className="text-[#00FFCC]" />
              <span>Pressure Tier Distribution</span>
            </h3>
            <span className="text-xs text-[#8B949E]">227.1k balls</span>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tierDistributionData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" hide />
                <YAxis
                  dataKey="tier"
                  type="category"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#8B949E', fontSize: 11 }}
                  width={110}
                />
                <Tooltip
                  content={({ payload }) => {
                    if (!payload || !payload.length) return null;
                    const data = payload[0].payload;
                    return (
                      <div className="bg-[#1C2128] border border-[#30363D] p-2.5 rounded-lg text-xs shadow-lg">
                        <div className="font-semibold text-white">{data.tier}</div>
                        <div className="text-[#8B949E] mt-1">
                          {data.count.toLocaleString()} deliveries ({data.pct}%)
                        </div>
                      </div>
                    );
                  }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {tierDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={TIER_COLORS[entry.tier] || '#00FFCC'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-[#8B949E] mt-3">
            Bimodal Pressure Metric combines match phase, RRR, wickets in hand, and projected totals without data leakage.
          </p>
        </div>

        {/* Top 5 Batters Mini Table */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-[#F0F6FC] flex items-center space-x-2">
              <Award size={18} className="text-[#00FFCC]" />
              <span>Top 5 Batters (FBPR)</span>
            </h3>
            <button
              onClick={() => onNavigate('batter-rankings')}
              className="text-xs text-[#00FFCC] hover:underline flex items-center space-x-1"
            >
              <span>View All</span>
              <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2.5">
            {topBatters.map((b) => (
              <div
                key={b.player_id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-[#0E1117] border border-[#21262D] hover:border-[#30363D] transition"
              >
                <div className="flex items-center space-x-3">
                  <span className="w-5 text-center text-xs font-bold text-[#8B949E] font-mono">
                    #{b.rank}
                  </span>
                  <div>
                    <div className="text-xs font-semibold text-[#F0F6FC]">
                      {b.player_name}
                    </div>
                    <div className="text-[10px] text-[#8B949E]">
                      {b.total_runs} runs • {b.strike_rate.toFixed(1)} SR
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-[#00FFCC]">
                    {b.final_fbpr.toFixed(2)}
                  </span>
                  <div className="text-[9px] text-[#8B949E]">FBPR</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top 5 Bowlers Mini Table */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-[#F0F6FC] flex items-center space-x-2">
              <ShieldCheck size={18} className="text-[#38BDF8]" />
              <span>Top 5 Bowlers (FBOR)</span>
            </h3>
            <button
              onClick={() => onNavigate('bowler-rankings')}
              className="text-xs text-[#38BDF8] hover:underline flex items-center space-x-1"
            >
              <span>View All</span>
              <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2.5">
            {topBowlers.map((bw) => (
              <div
                key={bw.player_id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-[#0E1117] border border-[#21262D] hover:border-[#30363D] transition"
              >
                <div className="flex items-center space-x-3">
                  <span className="w-5 text-center text-xs font-bold text-[#8B949E] font-mono">
                    #{bw.rank}
                  </span>
                  <div>
                    <div className="text-xs font-semibold text-[#F0F6FC]">
                      {bw.player_name}
                    </div>
                    <div className="text-[10px] text-[#8B949E]">
                      {bw.wickets_credited} wkts • {bw.economy_rate.toFixed(2)} Econ
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-[#38BDF8]">
                    {bw.final_fbor.toFixed(2)}
                  </span>
                  <div className="text-[9px] text-[#8B949E]">FBOR</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
