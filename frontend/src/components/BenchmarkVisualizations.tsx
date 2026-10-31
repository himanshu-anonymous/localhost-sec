import React from 'react';

interface BenchmarkVisProps {
  baselineAvail: number;
  adaptiveAvail: number;
  hardenedAvail: number;
  experimentalAvail: number;
  baselineBlast: number;
  adaptiveBlast: number;
  hardenedBlast: number;
  experimentalBlast: number;
  adaptiveContainment: string | number;
  rdiBaseline: number;
  rdiAdaptive: number;
}

export const BenchmarkVisualizations: React.FC<BenchmarkVisProps> = ({
  baselineAvail,
  adaptiveAvail,
  hardenedAvail,
  experimentalAvail,
  baselineBlast,
  adaptiveBlast,
  hardenedBlast,
  experimentalBlast,
  adaptiveContainment,
  rdiBaseline,
  rdiAdaptive
}) => {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs space-y-4">
      <div>
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          Benchmark visualizations
        </h2>
        <p className="text-[11px] text-slate-500">
          Availability, blast radius, containment, and RDI
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 1. Availability distribution */}
        <div className="border border-slate-100 rounded-lg p-4 bg-slate-50/40">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800 mb-3">
            <span>Availability distribution</span>
            <span className="text-[10px] text-slate-400 font-mono">% AVAILABILITY</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Baseline</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#1e293b] h-full" style={{ width: `${baselineAvail}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-slate-800">{baselineAvail.toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 font-bold text-[#dc2626] text-[11px]">Adaptive</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#dc2626] h-full" style={{ width: `${adaptiveAvail}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-[#dc2626]">{adaptiveAvail.toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Hardened</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#94a3b8] h-full" style={{ width: `${hardenedAvail}%` }} />
              </div>
              <span className="font-mono text-[11px] text-slate-700">{hardenedAvail.toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Experimental</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#cbd5e1] h-full" style={{ width: `${experimentalAvail}%` }} />
              </div>
              <span className="font-mono text-[11px] text-slate-700">{experimentalAvail.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* 2. Blast radius comparison */}
        <div className="border border-slate-100 rounded-lg p-4 bg-slate-50/40">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800 mb-3">
            <span>Blast radius comparison</span>
            <span className="text-[10px] text-slate-400 font-mono">BLAST RADIUS</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Baseline</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#1e293b] h-full" style={{ width: `${baselineBlast * 100}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-slate-800">{baselineBlast.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 font-bold text-[#dc2626] text-[11px]">Adaptive</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#dc2626] h-full" style={{ width: `${adaptiveBlast * 100}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-[#dc2626]">{adaptiveBlast.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Hardened</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#94a3b8] h-full" style={{ width: `${hardenedBlast * 100}%` }} />
              </div>
              <span className="font-mono text-[11px] text-slate-700">{hardenedBlast.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Experimental</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#cbd5e1] h-full" style={{ width: `${experimentalBlast * 100}%` }} />
              </div>
              <span className="font-mono text-[11px] text-slate-700">{experimentalBlast.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* 3. Containment time */}
        <div className="border border-slate-100 rounded-lg p-4 bg-slate-50/40">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800 mb-3">
            <span>Containment time</span>
            <span className="text-[10px] text-slate-400 font-mono">MTTC</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Baseline</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#dc2626] h-full w-full" />
              </div>
              <span className="font-mono text-[10px] font-bold text-[#dc2626]">UNCONTAINED 100s</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 font-bold text-[#dc2626] text-[11px]">Adaptive</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#dc2626] h-full w-[4%]" />
              </div>
              <span className="font-mono text-[11px] font-bold text-[#dc2626]">
                {typeof adaptiveContainment === 'number' ? `${adaptiveContainment.toFixed(1)}s` : adaptiveContainment}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Hardened</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#94a3b8] h-full w-[4%]" />
              </div>
              <span className="font-mono text-[11px] text-slate-700">0.0s</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Experimental</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#cbd5e1] h-full w-[12%]" />
              </div>
              <span className="font-mono text-[11px] text-slate-700">6.0s</span>
            </div>
          </div>
        </div>

        {/* 4. RDI comparison */}
        <div className="border border-slate-100 rounded-lg p-4 bg-slate-50/40">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800 mb-3">
            <span>RDI comparison</span>
            <span className="text-[10px] text-slate-400 font-mono">RDI</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Baseline</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#1e293b] h-full" style={{ width: `${Math.min(100, (rdiBaseline / 50) * 100)}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-slate-800">{rdiBaseline.toFixed(1)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 font-bold text-[#dc2626] text-[11px]">Adaptive</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#dc2626] h-full" style={{ width: `${Math.min(100, (rdiAdaptive / 50) * 100)}%` }} />
              </div>
              <span className="font-mono text-[11px] font-bold text-[#dc2626]">{rdiAdaptive.toFixed(1)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Hardened</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#94a3b8] h-full w-[7%]" />
              </div>
              <span className="font-mono text-[11px] text-slate-700">3.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-20 text-slate-600 text-[11px]">Experimental</span>
              <div className="flex-1 mx-3 bg-slate-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#cbd5e1] h-full w-[50%]" />
              </div>
              <span className="font-mono text-[11px] text-slate-700">25.2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

