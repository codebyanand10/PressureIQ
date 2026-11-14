import React from 'react';
import {
  BookOpen,
  Layers,
  Award,
  ShieldCheck,
  TrendingUp,
  Scale,
  FileText
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';

interface MethodologyViewProps {
  onNavigate: (page: PageId) => void;
}

export const MethodologyView: React.FC<MethodologyViewProps> = () => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal">Academic Rigor</Badge>
          <span className="text-xs text-[#8B949E] font-mono">SupeRR Selector Season 2</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1">
          Methodological Framework & Mathematical Foundations
        </h1>
        <p className="text-xs text-[#8B949E] mt-1 leading-relaxed">
          PressureIQ addresses the historical challenge of measuring clutch performance in Twenty20 cricket by developing an objective, physics-grounded pressure metric, coupled with empirical Bayes regularized player rating models.
        </p>
      </div>

      {/* 1. The Bimodal Pressure Model */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 space-y-4">
        <h2 className="text-lg font-black text-white flex items-center space-x-2">
          <TrendingUp size={20} className="text-[#00FFCC]" />
          <span>1. Bimodal Pressure Metric (P_t)</span>
        </h2>
        <p className="text-xs text-[#8B949E] leading-relaxed">
          Pressure is defined as a continuous scalar normalized to the closed interval [0, 1]. Crucially, cricket demands a bimodal architecture because the physical mechanics of chasing a known target differ fundamentally from setting an initial score.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0E1117] border border-[#21262D] space-y-3">
            <span className="text-xs font-bold text-[#00FFCC] uppercase tracking-wider block">
              Innings 2: Chase Dynamic Pressure
            </span>
            <div className="p-3 rounded-lg bg-[#161B22] border border-[#30363D] font-mono text-xs text-[#F0F6FC]">
              P_chase = 0.45 · f(RRR) + 0.35 · f(W_loss) + 0.20 · f(Balls)
            </div>
            <ul className="text-xs text-[#8B949E] space-y-1.5 list-disc list-inside">
              <li><strong className="text-white">f(RRR):</strong> Logistic scaling of Required Run Rate above 6.00 rpo.</li>
              <li><strong className="text-white">f(W_loss):</strong> Depletion of top-order wickets in hand.</li>
              <li><strong className="text-white">f(Balls):</strong> Exponential resource scarcity as overs elapse.</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-[#0E1117] border border-[#21262D] space-y-3">
            <span className="text-xs font-bold text-[#38BDF8] uppercase tracking-wider block">
              Innings 1: Target-Setting Volatility
            </span>
            <div className="p-3 rounded-lg bg-[#161B22] border border-[#30363D] font-mono text-xs text-[#F0F6FC]">
              P_first = 0.40 · f(Par_Deficit) + 0.35 · f(W_Rate) + 0.25 · f(Phase)
            </div>
            <ul className="text-xs text-[#8B949E] space-y-1.5 list-disc list-inside">
              <li><strong className="text-white">f(Par_Deficit):</strong> Projected total vs venue-adjusted par score.</li>
              <li><strong className="text-white">f(W_Rate):</strong> Cluster wicket loss acceleration.</li>
              <li><strong className="text-white">f(Phase):</strong> Exponential weight assigned to Death Overs (16-20).</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 2. Rating Engines: FBPR & FBOR */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* FBPR Batter Rating */}
        <div className="bg-[#161B22] border border-[#00FFCC]/30 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-black text-white flex items-center space-x-2">
            <Award size={20} className="text-[#00FFCC]" />
            <span>2. Final Batter Pressure Rating (FBPR)</span>
          </h2>
          <p className="text-xs text-[#8B949E]">
            Synthesizes four orthogonal dimensions into a comprehensive rating on a 0-100 scale:
          </p>

          <div className="p-3 rounded-lg bg-[#0E1117] border border-[#21262D] font-mono text-xs text-[#00FFCC]">
            Raw_FBPR = 0.35·Resilience + 0.30·Absolute + 0.20·Consistency + 0.15·Context
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Batting Resilience (35%)</span>
              <span className="text-[#8B949E]">Retention of strike rate vs personal baseline</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Absolute Scoring (30%)</span>
              <span className="text-[#8B949E]">Raw strike rate under high pressure</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Consistency (20%)</span>
              <span className="text-[#8B949E]">Standard deviation of innings output</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Context Leverage (15%)</span>
              <span className="text-[#8B949E]">Performance in Extreme vs High tier</span>
            </div>
          </div>
        </div>

        {/* FBOR Bowler Rating */}
        <div className="bg-[#161B22] border border-[#38BDF8]/30 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-black text-white flex items-center space-x-2">
            <ShieldCheck size={20} className="text-[#38BDF8]" />
            <span>3. Final Bowler Pressure Rating (FBOR)</span>
          </h2>
          <p className="text-xs text-[#8B949E]">
            Balances run suppression and game-changing wickets across critical bowling phases:
          </p>

          <div className="p-3 rounded-lg bg-[#0E1117] border border-[#21262D] font-mono text-xs text-[#38BDF8]">
            Raw_FBOR = 0.35·Restriction + 0.30·Breakthrough + 0.20·Consistency + 0.15·Phase
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Run Restriction (35%)</span>
              <span className="text-[#8B949E]">Economy containment relative to cohort par</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Breakthrough Threat (30%)</span>
              <span className="text-[#8B949E]">High-pressure wicket strike rate</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Consistency (20%)</span>
              <span className="text-[#8B949E]">Over-by-over variance control</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0E1117] border border-[#21262D]">
              <span className="text-white font-medium">Phase Leverage (15%)</span>
              <span className="text-[#8B949E]">Death overs and Powerplay high-leverage balls</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Empirical Bayes Shrinkage */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl p-6 space-y-4">
        <h2 className="text-lg font-black text-white flex items-center space-x-2">
          <Scale size={20} className="text-[#F59E0B]" />
          <span>4. Empirical Bayes Shrinkage & Uncertainty Bounds</span>
        </h2>
        <p className="text-xs text-[#8B949E] leading-relaxed">
          Small sample sizes in cricket analytics frequently produce spurious outliers. PressureIQ implements empirical Bayes shrinkage toward the population mean $\mu$, scaling each player's raw performance by their sample exposure $n_i$:
        </p>

        <div className="p-4 rounded-xl bg-[#0E1117] border border-[#21262D] font-mono text-xs text-[#F0F6FC] space-y-2">
          <div>S_i = n_i / (n_i + k)</div>
          <div className="text-[#F59E0B]">Final_Rating = S_i · Raw_Rating + (1 - S_i) · μ_cohort</div>
        </div>

        <p className="text-xs text-[#8B949E] leading-relaxed">
          For batters, $k = 40$ balls faced; for bowlers, $k = 60$ legal deliveries. Players with high sample sizes ($n_i \gg k$) retain their empirical score, while low-exposure players are shrunk conservatively to eliminate noise.
        </p>
      </div>
    </div>
  );
};
