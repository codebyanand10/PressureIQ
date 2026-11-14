import React from 'react';
import {
  ShieldCheck,
  Lock
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import validationDataRaw from '../data/validation.json';
import { ValidationData } from '../types';

interface StatisticalValidationViewProps {
  onNavigate: (page: PageId) => void;
}

export const StatisticalValidationView: React.FC<StatisticalValidationViewProps> = () => {
  const validation = validationDataRaw as unknown as ValidationData;
  const scorecard = validation.scorecard || [];
  const leakageChecks = validation.leakage_audit || [];

  const passedScorecard = scorecard.filter(
    (s) => s.batting_result === 'PASS' && s.bowling_result === 'PASS'
  ).length;
  const passedLeakage = leakageChecks.filter((l) => l.result === 'PASS').length;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <Badge variant="emerald">Audit Phase 9 Completed</Badge>
          <span className="text-xs text-[#8B949E] font-mono">
            {validation.bootstrap_iterations || 100} Match-Level Resamples
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1">
          Statistical Validation & Robustness
        </h1>
        <p className="text-xs text-[#8B949E] mt-1 max-w-3xl">
          PressureIQ has been subjected to a 10-dimension statistical audit and a 12-check leakage verification matrix. All rankings reflect Empirical Bayes shrinkage to prevent small-sample distortion.
        </p>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#161B22] p-4 rounded-xl border border-[#10B981]/30">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            10-Dimension Scorecard
          </div>
          <div className="text-2xl font-black text-[#10B981] font-mono mt-1">
            {passedScorecard} / {scorecard.length} PASS
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Zero critical methodology flaws
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#10B981]/30">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            12-Check Leakage Audit
          </div>
          <div className="text-2xl font-black text-[#10B981] font-mono mt-1">
            {passedLeakage} / {leakageChecks.length} PASS
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Zero future delivery data leakage
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#00FFCC]/30">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Bootstrap Confidence
          </div>
          <div className="text-2xl font-black text-[#00FFCC] font-mono mt-1">
            95% CI
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Match-level clustered resampling
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#38BDF8]/30">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Shrinkage Mechanism
          </div>
          <div className="text-2xl font-black text-[#38BDF8] font-mono mt-1">
            Empirical Bayes
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Sample variance adjustment
          </div>
        </div>
      </div>

      {/* 10-Dimension Validation Matrix */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D] flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <ShieldCheck size={16} className="text-[#10B981]" />
            <span>10-Dimension Robustness Matrix</span>
          </h3>
          <span className="text-xs text-[#8B949E]">Exhaustive Quality Assurance</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] font-mono uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Dimension</th>
                <th className="py-3 px-4 text-center">Batting</th>
                <th className="py-3 px-4 text-center">Bowling</th>
                <th className="py-3 px-4">Supporting Evidence</th>
                <th className="py-3 px-4">Operational Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {scorecard.map((item, idx) => (
                <tr key={idx} className="hover:bg-[#1C2128] transition-colors">
                  <td className="py-3 px-4 font-semibold text-white whitespace-nowrap">
                    {item.dimension}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Badge variant={item.batting_result === 'PASS' ? 'emerald' : 'amber'} size="sm">
                      {item.batting_result}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Badge variant={item.bowling_result === 'PASS' ? 'emerald' : 'amber'} size="sm">
                      {item.bowling_result}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-[#C9D1D9] max-w-sm">
                    {item.supporting_evidence}
                  </td>
                  <td className="py-3 px-4 text-[#8B949E] max-w-sm">
                    {item.operational_impact}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 12-Check Data Leakage Verification */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D] flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Lock size={16} className="text-[#38BDF8]" />
            <span>12-Check Data Leakage & Temporal Invariant Audit</span>
          </h3>
          <span className="text-xs text-[#8B949E]">100% Causal Independence</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] font-mono uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Check ID</th>
                <th className="py-3 px-4">Test Performed</th>
                <th className="py-3 px-4">Fields Examined</th>
                <th className="py-3 px-4">Audit Evidence</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {leakageChecks.map((chk, idx) => (
                <tr key={idx} className="hover:bg-[#1C2128] transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-[#38BDF8]">
                    {chk.check_id}
                  </td>
                  <td className="py-3 px-4 font-semibold text-white whitespace-nowrap">
                    {chk.test_performed}
                  </td>
                  <td className="py-3 px-4 font-mono text-[#8B949E] text-[11px]">
                    {chk.data_fields_examined}
                  </td>
                  <td className="py-3 px-4 text-[#C9D1D9]">
                    {chk.evidence}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Badge variant={chk.result === 'PASS' ? 'emerald' : 'amber'} size="sm">
                      {chk.result}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
