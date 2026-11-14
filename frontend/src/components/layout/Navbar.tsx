import React from 'react';
import {
  Activity,
  Award,
  Shield,
  User,
  Users,
  TrendingUp,
  CheckCircle2,
  BookOpen,
  Database,
  Menu,
  X,
  ExternalLink
} from 'lucide-react';

export type PageId =
  | 'overview'
  | 'batter-rankings'
  | 'bowler-rankings'
  | 'player-analysis'
  | 'player-comparison'
  | 'pressure-analysis'
  | 'validation'
  | 'methodology'
  | 'data-quality';

interface NavbarProps {
  activePage: PageId;
  onPageChange: (page: PageId) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activePage, onPageChange }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const navItems: Array<{ id: PageId; label: string; icon: React.ElementType }> = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'batter-rankings', label: 'Batter Rankings', icon: Award },
    { id: 'bowler-rankings', label: 'Bowler Rankings', icon: Shield },
    { id: 'player-analysis', label: 'Player Dossier', icon: User },
    { id: 'player-comparison', label: 'Comparison', icon: Users },
    { id: 'pressure-analysis', label: 'Pressure Engine', icon: TrendingUp },
    { id: 'validation', label: 'Robustness', icon: CheckCircle2 },
    { id: 'methodology', label: 'Methodology', icon: BookOpen },
    { id: 'data-quality', label: 'Data Quality', icon: Database },
  ];

  const handleSelect = (id: PageId) => {
    onPageChange(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-[#0E1117]/90 backdrop-blur-md border-b border-[#21262D]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => handleSelect('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#00FFCC] to-[#38BDF8] flex items-center justify-center shadow-lg shadow-[#00FFCC]/20 font-bold text-[#0E1117] text-xl">
              ⚡
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-black tracking-tight text-white font-mono">
                  Pressure<span className="text-[#00FFCC]">IQ</span>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-[#00FFCC]/10 text-[#00FFCC] border border-[#00FFCC]/30 tracking-wider uppercase">
                  v2.0 PRO
                </span>
              </div>
              <p className="text-[10px] text-[#8B949E] font-medium leading-none">
                SupeRR Selector Season 2 • Bimodal Analytics
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-[#161B22] text-[#00FFCC] border border-[#00FFCC]/30 shadow-sm'
                      : 'text-[#8B949E] hover:text-[#F0F6FC] hover:bg-[#161B22]/50'
                  }`}
                >
                  <Icon size={14} className={isActive ? 'text-[#00FFCC]' : 'text-[#8B949E]'} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Status Badge */}
          <div className="hidden md:flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#161B22] border border-[#30363D] text-xs">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
              <span className="text-[#8B949E] font-mono text-[11px]">582 Players Evaluated</span>
            </div>
          </div>

          {/* Mobile menu toggle */}
          <div className="flex lg:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-[#8B949E] hover:text-white hover:bg-[#161B22]"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-[#21262D] bg-[#161B22] px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelect(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? 'bg-[#00FFCC]/10 text-[#00FFCC] border border-[#00FFCC]/30'
                    : 'text-[#8B949E] hover:text-white'
                }`}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
