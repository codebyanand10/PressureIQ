import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'teal' | 'blue' | 'emerald' | 'amber' | 'red' | 'gray';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'teal',
  size = 'md',
}) => {
  const variantStyles = {
    teal: 'bg-[#00FFCC]/10 text-[#00FFCC] border-[#00FFCC]/30',
    blue: 'bg-[#38BDF8]/10 text-[#38BDF8] border-[#38BDF8]/30',
    emerald: 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30',
    amber: 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30',
    red: 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30',
    gray: 'bg-[#30363D]/40 text-[#8B949E] border-[#30363D]',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {children}
    </span>
  );
};
