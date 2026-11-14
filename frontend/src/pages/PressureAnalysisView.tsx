import React, { useState, useMemo } from 'react';
import {
  TrendingUp,
  Flame,
  Activity,
  Sliders,
  AlertCircle,
  HelpCircle,
  ShieldAlert
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  AreaChart,
  Area
} from 'recharts';

interface PressureAnalysisViewProps {
  onNavigate: (page: PageId) => void;
}

export const PressureAnalysisView: React.FC<PressureAnalysisViewProps> = () => {
  // Simulator State
  const [target, setTarget] = useState<number>(180);
  const [runsScored, setRunsScored] = useState<number>(120);
  const [ballsBowled, setBallsBowled] = useState<number>(84); // Over 14.0
  const [wicketsDown, setWicketsDown] = useState<number>(4);

  // Computed variables
  const runsRequired = Math.max(0, target - runsScored);
  const ballsRemaining = Math.max(1, 120 - ballsBowled);
  const wicketsRemaining = Math.max(0, 10 - wicketsDown);
  const rrr = (runsRequired / ballsRemaining) * 6;

  // Bimodal Pressure Calculation Simulation
  const simulatedPressure = useMemo(() => {
    // Phase weight
    const phaseWeight = ballsBowled < 36 ? 0.2 : ballsBowled < 90 ? 0.3 : 0.5;
    // RRR pressure component
    const rrrPressure = Math.min(1.0, Math.max(0, (rrr - 6) / 10));
    // Wicket risk component
    const wicketPressure = (10 - wicketsRemaining) / 10;
    // Ball scarcity component
    const ballScarcity = (120 - ballsRemaining) / 120;

    const raw = 0.45 * rrrPressure + 0.35 * wicketPressure + 0.20 * ballScarcity;
    return Math.min(1.0, Math.max(0, raw));
  }, [rrr, wicketsRemaining, ballsRemaining, ballsBowled]);

  const pressureTier = useMemo(() => {
    if (simulatedPressure >= 0.85) return { label: 'Extreme Pressure', color: '#A855F7', badge: 'red' as const };
    if (simulatedPressure >= 0.65) return { label: 'High Pressure', color: '#EF4444', badge: 'amber' as const };
    if (simulatedPressure >= 0.35) return { label: 'Medium Pressure', color: '#F59E0B', badge: 'blue' as const };
    return { label: 'Low Pressure', color: '#38BDF8', badge: 'teal' as const };
  }, [simulatedPressure]);

  // Generate synthetic trajectory data for chart
  const trajectoryData = useMemo(() => {
    const points = [];
    for (let over = 1; over <= 20; over++) {
      const bRemaining = 120 - over * 6;
      const baseRRR = 7 + (over > 14 ? (over - 14) * 1.5 : 0);
      const press = Math.min(
        1.0,
        0.15 + (over / 20) * 0.4 + (baseRRR > 10 ? (baseRRR - 10) * 0.08 : 0)
      );
      points.push({
        over: `Over ${over}`,
        pressure: Number(press.toFixed(2)),
        rrr: Number(baseRRR.toFixed(1)),
      });
    }
    return points;
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal">Core Engine Architecture</Badge>
          <span className="text-xs text-[#8B949E] font-mono">Zero Future Data Leakage</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1">
          Bimodal Pressure Detection Engine
        </h1>
        <p className="text-xs text-[#8B949E] mt-1 max-w-3xl">
          Cricket matches exhibit distinct physical regimes between 1st innings target-setting and 2nd innings chasing. PressureIQ formulates separate bimodal equations respecting match phase, resource scarcity, and historical win curves without leaking delivery outcomes.
        </p>
      </div>

      {/* Interactive Match Situation Simulator */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Sliders size={18} className="text-[#00FFCC]" />
            <span>Interactive Chase Pressure Simulator</span>
          </h3>
          <Badge variant={pressureTier.badge}>{pressureTier.label}</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {/* Target */}
          <div>
            <label className="text-xs text-[#8B949E] font-medium block mb-2">
              Target Score: <strong className="text-white font-mono">{target}</strong>
            </label>
            <input
              type="range"
              min="120"
              max="240"
              step="5"
              value={target}
              onChange={(e) => setTarget(Number(e.target.value))}
              className="w-full accent-[#00FFCC]"
            />
          </div>

          {/* Runs Scored */}
          <div>
            <label className="text-xs text-[#8B949E] font-medium block mb-2">
              Runs Scored: <strong className="text-white font-mono">{runsScored}</strong>
            </label>
            <input
              type="range"
              min="0"
              max={target}
              step="2"
              value={runsScored}
              onChange={(e) => setRunsScored(Number(e.target.value))}
              className="w-full accent-[#00FFCC]"
            />
          </div>

          {/* Overs Bowled */}
          <div>
            <label className="text-xs text-[#8B949E] font-medium block mb-2">
              Overs Bowled: <strong className="text-white font-mono">{(ballsBowled / 6).toFixed(1)}</strong> ({ballsRemaining} balls left)
            </label>
            <input
              type="range"
              min="6"
              max="118"
              step="6"
              value={ballsBowled}
              onChange={(e) => setBallsBowled(Number(e.target.value))}
              className="w-full accent-[#00FFCC]"
            />
          </div>

          {/* Wickets Down */}
          <div>
            <label className="text-xs text-[#8B949E] font-medium block mb-2">
              Wickets Fallen: <strong className="text-white font-mono">{wicketsDown}</strong> ({wicketsRemaining} in hand)
            </label>
            <input
              type="range"
              min="0"
              max="9"
              step="1"
              value={wicketsDown}
              onChange={(e) => setWicketsDown(Number(e.target.value))}
              className="w-full accent-[#00FFCC]"
            />
          </div>
        </div>

        {/* Live Simulation Output Box */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-[#0E1117] p-5 rounded-xl border border-[#21262D]">
          <div>
            <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
              Required Run Rate (RRR)
            </div>
            <div className="text-2xl font-black text-white font-mono mt-0.5">
              {rrr.toFixed(2)}
            </div>
            <div className="text-[10px] text-[#8B949E] mt-0.5">
              Need {runsRequired} runs from {ballsRemaining} balls
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
              Wickets in Hand
            </div>
            <div className="text-2xl font-black text-white font-mono mt-0.5">
              {wicketsRemaining}
            </div>
            <div className="text-[10px] text-[#8B949E] mt-0.5">
              Resource factor: {(wicketsRemaining / 10).toFixed(2)}
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
              Pressure Index (P_t)
            </div>
            <div
              className="text-2xl font-black font-mono mt-0.5"
              style={{ color: pressureTier.color }}
            >
              {simulatedPressure.toFixed(3)}
            </div>
            <div className="text-[10px] text-[#8B949E] mt-0.5">
              On 0.00 to 1.00 continuous scale
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono tracking-wider text-[#8B949E]">
              Classification Tier
            </div>
            <div
              className="text-base font-bold mt-1.5"
              style={{ color: pressureTier.color }}
            >
              {pressureTier.label}
            </div>
            <div className="text-[10px] text-[#8B949E] mt-0.5">
              {simulatedPressure >= 0.65 ? 'Qualifies as High Pressure' : 'Normal match phase'}
            </div>
          </div>
        </div>
      </div>

      {/* Trajectory Curve Chart & Mathematical Definitions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trajectory Area Chart */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-2">
            Chase Pressure Dynamic Trajectory
          </h3>
          <p className="text-xs text-[#8B949E] mb-4">
            Simulated 20-over escalation showing exponential sensitivity as overs decay.
          </p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trajectoryData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="pressureGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00FFCC" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#00FFCC" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#21262D" strokeDasharray="3 3" />
                <XAxis dataKey="over" stroke="#484F58" tick={{ fill: '#8B949E', fontSize: 10 }} />
                <YAxis domain={[0, 1]} stroke="#484F58" tick={{ fill: '#8B949E', fontSize: 10 }} />
                <Tooltip
                  content={({ payload }) => {
                    if (!payload || !payload.length) return null;
                    const d = payload[0].payload;
                    return (
                      <div className="bg-[#1C2128] border border-[#30363D] p-2 rounded text-xs space-y-1">
                        <div className="text-white font-semibold">{d.over}</div>
                        <div className="text-[#00FFCC]">Pressure Score: {d.pressure}</div>
                        <div className="text-[#38BDF8]">Required RR: {d.rrr}</div>
                      </div>
                    );
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="pressure"
                  stroke="#00FFCC"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#pressureGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bimodal Regime Breakdown */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-white">
            Bimodal Mathematical Regimes
          </h3>

          <div className="p-4 rounded-xl bg-[#0E1117] border border-[#21262D] space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-[#00FFCC]">
              <Flame size={14} />
              <span>Innings 2: Deterministic Target Chase</span>
            </div>
            <p className="text-xs text-[#8B949E] leading-relaxed">
              Pressure is governed by the instant ratio between Required Run Rate and Current Resource Availability:
            </p>
            <div className="p-2.5 rounded bg-[#161B22] font-mono text-[11px] text-[#C9D1D9] border border-[#30363D]">
              P_chase = 0.45 · f(RRR) + 0.35 · (10 - W)/10 + 0.20 · (120 - B)/120
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#0E1117] border border-[#21262D] space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-[#38BDF8]">
              <ShieldAlert size={14} />
              <span>Innings 1: Par Score Deficiency & Phase Volatility</span>
            </div>
            <p className="text-xs text-[#8B949E] leading-relaxed">
              Target is unknown; pressure is derived from projected totals relative to venue-adjusted par score:
            </p>
            <div className="p-2.5 rounded bg-[#161B22] font-mono text-[11px] text-[#C9D1D9] border border-[#30363D]">
              P_first = 0.40 · max(0, Par - Projected)/Par + 0.35 · WicketLossRate + 0.25 · PhaseWeight
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
