import React from 'react';

interface MetricsCardsProps {
  adaptiveAvailability: number;
  baselineAvailability: number;
  containmentTime: number | string;
  adaptiveBlastRadius: number;
  baselineBlastRadius: number;
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({
  adaptiveAvailability,
  baselineAvailability,
  containmentTime,
  adaptiveBlastRadius,
  baselineBlastRadius
}) => {
  const diffPp = (adaptiveAvailability - baselineAvailability).toFixed(1);
  const diffSign = (adaptiveAvailability - baselineAvailability) >= 0 ? '+' : '';

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* 1. ADAPTIVE AVAILABILITY - Solid Red Card */}
      <div className="bg-[#dc2626] text-white p-5 rounded-lg shadow-sm flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold tracking-wider uppercase text-red-100 block">
            ADAPTIVE AVAILABILITY
          </span>
          <div className="text-3xl font-extrabold tracking-tight mt-1">
            {adaptiveAvailability.toFixed(1)}%
          </div>
        </div>
        <div className="text-[11px] font-semibold text-red-200 mt-3">
          DDPS + PPO
        </div>
      </div>

      {/* 2. AVAILABILITY DIFFERENCE - White Card */}
      <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block">
            AVAILABILITY DIFFERENCE
          </span>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
            {diffSign}{diffPp} pp
          </div>
        </div>
        <div className="text-[11px] text-slate-500 mt-3">
          Adaptive vs. baseline: {baselineAvailability.toFixed(1)}%
        </div>
      </div>

      {/* 3. TIME TO CONTAIN - White Card */}
      <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block">
            TIME TO CONTAIN
          </span>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
            {typeof containmentTime === 'number' ? `${containmentTime.toFixed(1)}s` : containmentTime}
          </div>
        </div>
        <div className="text-[11px] text-slate-500 mt-3">
          Adaptive: lateral pivot contained
        </div>
      </div>

      {/* 4. ADAPTIVE BLAST RADIUS - White Card */}
      <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block">
            ADAPTIVE BLAST RADIUS
          </span>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
            {adaptiveBlastRadius.toFixed(2)}
          </div>
        </div>
        <div className="text-[11px] text-slate-500 mt-3">
          Baseline blast radius: {baselineBlastRadius.toFixed(2)}
        </div>
      </div>
    </div>
  );
};

