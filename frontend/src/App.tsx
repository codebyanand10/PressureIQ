import React, { useState, Component, ErrorInfo, ReactNode } from 'react';
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
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('PressureIQ ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0E1117] flex items-center justify-center p-6 text-white">
          <div className="max-w-md w-full bg-[#161B22] border border-[#EF4444]/40 rounded-2xl p-6 text-center shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-[#EF4444]/10 text-[#EF4444] mx-auto flex items-center justify-center mb-4">
              <AlertCircle size={28} />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Something went wrong</h2>
            <p className="text-xs text-[#8B949E] mb-4">
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-[#00FFCC] text-[#0E1117] font-bold text-xs hover:bg-[#00CC99] transition"
            >
              <RefreshCw size={14} />
              <span>Reload Application</span>
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export function App() {
  const [activePage, setActivePage] = useState<PageId>('overview');
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>(undefined);

  const handleSelectPlayer = (id: string) => {
    setSelectedPlayerId(id);
    setActivePage('player-analysis');
  };

  return (
    <ErrorBoundary>
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
    </ErrorBoundary>
  );
}

export default App;
