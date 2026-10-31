import React from 'react';
import { ShieldCheck, Lock, Info, Sparkles } from 'lucide-react';

interface AvailabilitySectionProps {
  baselineAvail: number;
  adaptiveAvail: number;
  hardenedAvail: number;
  experimentalAvail: number;
  invariantViolations?: number;
}

export const AvailabilitySection: React.FC<AvailabilitySectionProps> = ({
  baselineAvail,
  adaptiveAvail,
  hardenedAvail,
  experimentalAvail,
  invariantViolations = 0
}) => {
  const diff = (adaptiveAvail - baselineAvail).toFixed(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left: Availability under concurrent attack */}
      <div className="lg:col-span-2 bg-white border border-slate-200 p-6 rounded-lg shadow-2xs">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">
            Availability under concurrent attack
          </h2>
        </div>
        <p className="text-[11px] text-slate-500 mb-6">
          Black Sky CI/CD - Four-way synchronous benchmark
        </p>

        {/* Axis Scale Markers */}
        <div className="relative pl-24 pr-16 mb-2">
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>0</span>
            <span>25</span>
            <span>50</span>
            <span>75</span>
            <span>100%</span>
          </div>
          {/* Subtle grid lines */}
          <div className="w-full h-px bg-slate-100 mt-1" />
        </div>

        {/* Bars Container */}
        <div className="space-y-4">
          {/* 1. Baseline */}
          <div className="flex items-center gap-4">
            <span className="w-20 text-xs font-semibold text-slate-700 text-left">Baseline</span>
            <div className="flex-1 bg-slate-100 h-6 rounded overflow-hidden relative">
              <div 
                className="bg-[#1e293b] h-full transition-all duration-500 flex items-center px-2"
                style={{ width: `${Math.min(100, Math.max(5, baselineAvail))}%` }}
              >
                {baselineAvail < 60 && (
                  <span className="text-[9px] font-bold text-red-300 uppercase tracking-wider">
                    BREACH
                  </span>
                )}
              </div>
            </div>
            <span className="w-12 text-right text-xs font-bold text-slate-800 font-mono">
              {baselineAvail.toFixed(1)}%
            </span>
          </div>

          {/* 2. Adaptive (Selected Policy) */}
          <div className="flex items-center gap-4">
            <span className="w-20 text-xs font-bold text-[#dc2626] text-left">Adaptive</span>
            <div className="flex-1 bg-slate-100 h-6 rounded overflow-hidden relative">
              <div 
                className="bg-[#dc2626] h-full transition-all duration-500 flex items-center px-2.5 shadow-sm"
                style={{ width: `${Math.min(100, Math.max(5, adaptiveAvail))}%` }}
              >
                <span className="text-[9px] font-bold text-white uppercase tracking-wider">
                  SELECTED POLICY
                </span>
              </div>
            </div>
            <span className="w-12 text-right text-xs font-extrabold text-[#dc2626] font-mono">
              {adaptiveAvail.toFixed(1)}%
            </span>
          </div>

          {/* 3. Hardened */}
          <div className="flex items-center gap-4">
            <span className="w-20 text-xs font-medium text-slate-600 text-left">Hardened</span>
            <div className="flex-1 bg-slate-100 h-6 rounded overflow-hidden relative">
              <div 
                className="bg-[#94a3b8] h-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(5, hardenedAvail))}%` }}
              />
            </div>
            <span className="w-12 text-right text-xs font-bold text-slate-800 font-mono">
              {hardenedAvail.toFixed(1)}%
            </span>
          </div>

          {/* 4. Experimental */}
          <div className="flex items-center gap-4">
            <span className="w-20 text-xs font-medium text-slate-600 text-left">Experimental</span>
            <div className="flex-1 bg-slate-100 h-6 rounded overflow-hidden relative">
              <div 
                className="bg-[#cbd5e1] h-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(5, experimentalAvail))}%` }}
              />
            </div>
            <span className="w-12 text-right text-xs font-bold text-slate-800 font-mono">
              {experimentalAvail.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Difference callout in red */}
        <div className="mt-6 pt-4 border-t border-slate-100 text-xs font-bold text-[#dc2626] flex items-center gap-1.5">
          <span>+{diff} pp</span>
          <span className="font-normal text-slate-700">Adaptive maintained availability and contained the lateral pivot.</span>
        </div>
      </div>

      {/* Right: DDPS / Invariant Guard */}
      <div className="bg-white border border-slate-200 p-6 rounded-lg shadow-2xs flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              DDPS / invariant guard
            </h2>
            <ShieldCheck className="w-4 h-4 text-[#dc2626]" />
          </div>

          {/* Omega preservation banner */}
          <div className="flex items-start gap-3 p-3 bg-red-50/50 border border-red-100 rounded-md mb-4">
            <div className="w-8 h-8 rounded-full bg-[#dc2626] text-white font-serif font-bold text-sm flex items-center justify-center shrink-0">
              Ω
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">
                Security Invariants preserved
              </div>
              <div className="text-[10px] text-[#dc2626] font-bold tracking-wider uppercase">
                POLICY SANCTUARY - ADAPTIVE
              </div>
            </div>
          </div>

          <p className="text-[11px] text-slate-600 leading-relaxed mb-4">
            The Dynamic Defensive Policy Stack adjusts cross-layer control priorities without violating Ω.
          </p>

          {/* Policy meta details */}
          <div className="space-y-2 border-t border-slate-100 pt-3 text-xs">
            <div className="flex items-center justify-between py-1">
              <span className="text-slate-500 text-[11px]">Policy focus</span>
              <span className="bg-[#dc2626] text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-wide">
                ADAPTIVE
              </span>
            </div>
            <div className="flex items-center justify-between py-1">
              <span className="text-slate-500 text-[11px]">Control engine</span>
              <span className="text-slate-800 font-mono text-[11px] font-semibold">
                DDPS + PPO
              </span>
            </div>
          </div>
        </div>

        {/* Human approval and Domain C note */}
        <div className="space-y-2 border-t border-slate-100 pt-3 mt-4">
          <div className="flex items-center gap-2 text-[11px] text-slate-700 font-medium">
            <Lock className="w-3 h-3 text-[#dc2626]" />
            <span>Human approval before cyber-range emission</span>
          </div>
          <div className="p-2.5 bg-slate-50 border border-slate-200/60 rounded text-[10px] text-slate-500 leading-relaxed flex items-start gap-1.5">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <span>
              Domain C provides out-of-band explanations and root-cause analysis, not an inline policy enforcement step.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

