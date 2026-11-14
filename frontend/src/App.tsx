import React, { useState } from 'react';
import { Navbar, PageId } from './components/layout/Navbar';
import { OverviewView } from './pages/OverviewView';
import { BatterRankingsView } from './pages/BatterRankingsView';
import { BowlerRankingsView } from './pages/BowlerRankingsView';
import { PlayerAnalysisView } from './pages/PlayerAnalysisView';
import { PlayerComparisonView } from './pages/PlayerComparisonView';
import { PressureAnalysisView } from './pages/PressureAnalysisView';
import { StatisticalValidationView } from './pages/StatisticalValidationView';
import { MethodologyView } from './pages/MethodologyView';
import { DataQualityView } from './pages/DataQualityView';

export function App() {
  const [activePage, setActivePage] = useState<PageId>('overview');
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>(undefined);

  const handleSelectPlayer = (id: string) => {
    setSelectedPlayerId(id);
    setActivePage('player-analysis');
  };

  return (
    <div className="min-h-screen bg-[#0E1117] text-[#F0F6FC] flex flex-col font-sans selection:bg-[#00FFCC]/20 selection:text-[#00FFCC]">
      {/* Navigation Header */}
      <Navbar activePage={activePage} onPageChange={setActivePage} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activePage === 'overview' && (
          <OverviewView onNavigate={setActivePage} />
        )}
        {activePage === 'batter-rankings' && (
          <BatterRankingsView
            onNavigate={setActivePage}
            onSelectPlayer={handleSelectPlayer}
          />
        )}
        {activePage === 'bowler-rankings' && (
          <BowlerRankingsView
            onNavigate={setActivePage}
            onSelectPlayer={handleSelectPlayer}
          />
        )}
        {activePage === 'player-analysis' && (
          <PlayerAnalysisView
            initialPlayerId={selectedPlayerId}
            onNavigate={setActivePage}
          />
        )}
        {activePage === 'player-comparison' && (
          <PlayerComparisonView onNavigate={setActivePage} />
        )}
        {activePage === 'pressure-analysis' && (
          <PressureAnalysisView onNavigate={setActivePage} />
        )}
        {activePage === 'validation' && (
          <StatisticalValidationView onNavigate={setActivePage} />
        )}
        {activePage === 'methodology' && (
          <MethodologyView onNavigate={setActivePage} />
        )}
        {activePage === 'data-quality' && (
          <DataQualityView onNavigate={setActivePage} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#21262D] bg-[#0E1117] py-8 text-xs text-[#8B949E]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-white font-mono">PressureIQ</span>
            <span>•</span>
            <span>SupeRR Selector Season 2 Official Analytics Submission</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-[11px] font-mono text-[#00FFCC]">
              Bimodal Physics • Empirical Bayes • 95% Bootstrap CI
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
