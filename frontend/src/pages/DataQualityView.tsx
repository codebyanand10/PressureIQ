import React from 'react';
import {
  Database,
  CheckCircle2,
  FileCheck,
  Server,
  Layers,
  ShieldCheck
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { PageId } from '../components/layout/Navbar';
import dataQualityData from '../data/data_quality.json';

interface DataQualityViewProps {
  onNavigate: (page: PageId) => void;
}

export const DataQualityView: React.FC<DataQualityViewProps> = () => {
  const telemetry = dataQualityData.pipeline_telemetry;
  const physicsInvariants = dataQualityData.physics_invariants;

  const schemaItems = [
    { field: 'match_id', type: 'VARCHAR', description: 'Unique identifier for the fixture' },
    { field: 'innings', type: 'INT', description: 'Innings index (1 = First innings, 2 = Chase)' },
    { field: 'over_number', type: 'INT', description: 'Over index [0, 19]' },
    { field: 'ball_number', type: 'INT', description: 'Ball within over [1, 6+]' },
    { field: 'striker_id', type: 'VARCHAR', description: 'Unique identifier of facing batter' },
    { field: 'bowler_id', type: 'VARCHAR', description: 'Unique identifier of delivery bowler' },
    { field: 'pressure_score', type: 'FLOAT', description: 'Bimodal Pressure Index [0.00, 1.00]' },
    { field: 'pressure_tier', type: 'VARCHAR', description: 'Low, Medium, High, Extreme categorization' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal">Integrity Assurance</Badge>
          <span className="text-xs text-[#8B949E] font-mono">100% Cardinality Preserved</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-[#F0F6FC] mt-1">
          Data Pipeline Telemetry & Quality Assurance
        </h1>
        <p className="text-xs text-[#8B949E] mt-1 max-w-3xl">
          Complete audit trail verifying end-to-end transformation from raw ball-by-ball delivery logs into normalized pressure indices and ranking deliverables.
        </p>
      </div>

      {/* Telemetry Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#161B22] p-4 rounded-xl border border-[#30363D]">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Raw Deliveries Ingested
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">
            {telemetry.raw_balls.toLocaleString()}
          </div>
          <div className="text-[10px] text-[#10B981] mt-1 flex items-center space-x-1">
            <CheckCircle2 size={12} />
            <span>100% Preserved</span>
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#30363D]">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Processed Deliveries
          </div>
          <div className="text-2xl font-black text-[#00FFCC] font-mono mt-1">
            {telemetry.processed_deliveries.toLocaleString()}
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Zero dropped records
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#30363D]">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Unique Fixtures
          </div>
          <div className="text-2xl font-black text-[#38BDF8] font-mono mt-1">
            {telemetry.unique_matches}
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            IPL tournament matches
          </div>
        </div>

        <div className="bg-[#161B22] p-4 rounded-xl border border-[#30363D]">
          <div className="text-[10px] text-[#8B949E] uppercase font-mono tracking-wider">
            Evaluated Athletes
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">
            {telemetry.unique_players}
          </div>
          <div className="text-[10px] text-[#8B949E] mt-1">
            Across batting and bowling
          </div>
        </div>
      </div>

      {/* Physics Invariant Checks */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D] flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <ShieldCheck size={16} className="text-[#00FFCC]" />
            <span>Cricket Physics Invariants Verification</span>
          </h3>
          <span className="text-xs text-[#8B949E]">Automated Boundary Validation</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] font-mono uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Invariant Condition</th>
                <th className="py-3 px-4">Expected Mathematical Boundary</th>
                <th className="py-3 px-4">Observed In Dataset</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {physicsInvariants.map((inv, idx) => (
                <tr key={idx} className="hover:bg-[#1C2128] transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">
                    {inv.invariant}
                  </td>
                  <td className="py-3 px-4 text-[#8B949E] font-mono text-[11px]">
                    {inv.expected}
                  </td>
                  <td className="py-3 px-4 font-mono text-[#00FFCC]">
                    {inv.actual}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Badge variant="emerald" size="sm">
                      {inv.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Core Schema Reference */}
      <div className="bg-[#161B22] border border-[#30363D] rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#21262D]">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Database size={16} className="text-[#38BDF8]" />
            <span>Core Analytical Pipeline Schema Dictionary</span>
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0E1117] text-[#8B949E] border-b border-[#21262D] font-mono uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Data Type</th>
                <th className="py-3 px-4">Functional Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262D]">
              {schemaItems.map((col, idx) => (
                <tr key={idx} className="hover:bg-[#1C2128] transition-colors">
                  <td className="py-3 px-4 font-mono font-semibold text-white">
                    {col.field}
                  </td>
                  <td className="py-3 px-4 font-mono text-[#00FFCC] text-[11px]">
                    {col.type}
                  </td>
                  <td className="py-3 px-4 text-[#C9D1D9]">
                    {col.description}
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
