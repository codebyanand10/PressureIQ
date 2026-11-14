import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  icon?: LucideIcon;
  variant?: 'teal' | 'blue' | 'emerald' | 'amber' | 'default';
  trend?: {
    value: string;
    positive?: boolean;
  };
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subValue,
  icon: Icon,
  variant = 'default',
  trend,
}) => {
  const borderVariants = {
    teal: 'border-[#00FFCC]/20 hover:border-[#00FFCC]/40',
    blue: 'border-[#38BDF8]/20 hover:border-[#38BDF8]/40',
    emerald: 'border-[#10B981]/20 hover:border-[#10B981]/40',
    amber: 'border-[#F59E0B]/20 hover:border-[#F59E0B]/40',
    default: 'border-[#30363D] hover:border-[#484F58]',
  };

  const iconColors = {
    teal: 'text-[#00FFCC] bg-[#00FFCC]/10',
    blue: 'text-[#38BDF8] bg-[#38BDF8]/10',
    emerald: 'text-[#10B981] bg-[#10B981]/10',
    amber: 'text-[#F59E0B] bg-[#F59E0B]/10',
    default: 'text-[#8B949E] bg-[#21262D]',
  };

  return (
    <div
      className={`bg-[#161B22] rounded-xl p-5 border transition-all duration-200 shadow-sm ${borderVariants[variant]}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs uppercase tracking-wider font-semibold text-[#8B949E]">
          {label}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg ${iconColors[variant]}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="flex items-baseline space-x-2">
        <div className="text-2xl font-bold text-[#F0F6FC] font-mono">
          {value}
        </div>
        {trend && (
          <span
            className={`text-xs font-semibold ${
              trend.positive ? 'text-[#10B981]' : 'text-[#EF4444]'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>
      {subValue && (
        <div className="text-xs text-[#8B949E] mt-1.5">{subValue}</div>
      )}
    </div>
  );
};
