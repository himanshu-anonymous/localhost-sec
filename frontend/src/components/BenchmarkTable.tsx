import React from 'react';
import { Check, AlertTriangle, ShieldAlert, ArrowUpRight } from 'lucide-react';

interface BenchmarkTableProps {
  baselineAvail: number;
  adaptiveAvail: number;
  hardenedAvail: number;
  experimentalAvail: number;
  baselineBlast: number;
  adaptiveBlast: number;
  hardenedBlast: number;
  experimentalBlast: number;
  mttcAdaptive: string | number;
  rdiAdaptive: number;
  rdiBaseline: number;
  onSelectInstance?: (instanceId: string) => void;
}

export const BenchmarkTable: React.FC<BenchmarkTableProps> = ({
  baselineAvail,
  adaptiveAvail,
  hardenedAvail,
  experimentalAvail,
  baselineBlast,
  adaptiveBlast,
  hardenedBlast,
  experimentalBlast,
  mttcAdaptive,
  rdiAdaptive,
  rdiBaseline,
  onSelectInstance
}) => {
  const rows = [
    {
      id: 'env_a_baseline',
      name: 'Baseline',
      isAdaptive: false,
      policy: 'Permissive static',
      availability: `${baselineAvail.toFixed(1)}%`,
      blastRadius: baselineBlast.toFixed(2),
      mttc: 'UNCONTAINED (Breach)',
      mttcClass: 'text-[#dc2626] font-semibold',
      rdi: rdiBaseline.toFixed(1),
      outcome: 'Breach',
      outcomeBadge: 'bg-red-50 text-[#dc2626] border border-red-200'
    },
    {
      id: 'env_b_adaptive',
      name: 'Adaptive',
      isAdaptive: true,
      policy: 'DDPS + PPO',
      availability: `${adaptiveAvail.toFixed(1)}%`,
      blastRadius: adaptiveBlast.toFixed(2),
      mttc: typeof mttcAdaptive === 'number' ? `${mttcAdaptive.toFixed(1)}s` : mttcAdaptive,
      mttcClass: 'text-slate-700',
      rdi: rdiAdaptive.toFixed(1),
      outcome: 'Contained',
      outcomeBadge: 'bg-slate-100 text-slate-700 border border-slate-200'
    },
    {
      id: 'env_c_hardened',
      name: 'Hardened',
      isAdaptive: false,
      policy: 'Strict static',
      availability: `${hardenedAvail.toFixed(1)}%`,
      blastRadius: hardenedBlast.toFixed(2),
      mttc: '0.0s',
      mttcClass: 'text-slate-700',
      rdi: '3.5',
      outcome: 'Contained',
      outcomeBadge: 'bg-slate-100 text-slate-700 border border-slate-200'
    },
    {
      id: 'env_d_experimental',
      name: 'Experimental',
      isAdaptive: false,
      policy: 'AI tuning',
      availability: `${experimentalAvail.toFixed(1)}%`,
      blastRadius: experimentalBlast.toFixed(2),
      mttc: '6.0s',
      mttcClass: 'text-slate-700',
      rdi: '25.2',
      outcome: 'Contained',
      outcomeBadge: 'bg-slate-100 text-slate-700 border border-slate-200'
    }
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
      {/* Title & Attack Badges */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">
            Black Sky CI/CD benchmark
          </h2>
          <div className="flex items-center gap-2 mt-2 text-xs text-slate-500 font-medium">
            <span className="text-[11px] text-slate-400 font-mono uppercase">VECTORS:</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">Edge DDoS</span>
            <span className="text-slate-300">/</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">Auth Stuffing</span>
            <span className="text-slate-300">/</span>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">Lateral CI exploitation</span>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 font-medium self-start sm:self-auto">
          4 environments (click row to inspect)
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-200 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              <th className="py-2.5 px-3">ENVIRONMENT</th>
              <th className="py-2.5 px-3">POLICY</th>
              <th className="py-2.5 px-3">AVAILABILITY ↑</th>
              <th className="py-2.5 px-3">BLAST RADIUS ↓</th>
              <th className="py-2.5 px-3">MTTC ↓</th>
              <th className="py-2.5 px-3">RDI ↓</th>
              <th className="py-2.5 px-3">OUTCOME</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => (
              <tr 
                key={row.id} 
                onClick={() => onSelectInstance && onSelectInstance(row.id)}
                className={`transition-colors cursor-pointer ${
                  row.isAdaptive 
                    ? 'bg-red-50/40 font-medium text-slate-900 hover:bg-red-50/70' 
                    : 'hover:bg-slate-50 text-slate-700'
                }`}
              >
                <td className="py-3 px-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${row.isAdaptive ? 'bg-[#dc2626]' : 'bg-slate-400'}`} />
                    <span className={row.isAdaptive ? 'font-bold text-[#dc2626] flex items-center gap-1' : 'font-semibold'}>
                      {row.name}
                      {row.isAdaptive && <Check className="w-3.5 h-3.5 text-[#dc2626]" />}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">{row.policy}</td>
                <td className="py-3 px-3 font-bold font-mono text-slate-900">{row.availability}</td>
                <td className="py-3 px-3 font-mono text-slate-600">{row.blastRadius}</td>
                <td className={`py-3 px-3 font-mono text-[11px] ${row.mttcClass}`}>{row.mttc}</td>
                <td className="py-3 px-3 font-mono text-slate-600">{row.rdi}</td>
                <td className="py-3 px-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded tracking-wide ${row.outcomeBadge}`}>
                      {row.outcome}
                    </span>
                    <ArrowUpRight className="w-3 h-3 text-slate-400 opacity-60 ml-2" />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer Notes */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100 text-[10px] text-slate-400">
        <span>Identical attack seeds across all environments</span>
        <span>* Higher is better / v Lower is better</span>
      </div>
    </div>
  );
};
