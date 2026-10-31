import React from 'react';
import { Shield, ShieldAlert, Cpu, Lock, ArrowUpRight, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';

interface InstanceCardsProps {
  baselineAvail: number;
  adaptiveAvail: number;
  hardenedAvail: number;
  experimentalAvail: number;
  baselineBlast: number;
  adaptiveBlast: number;
  hardenedBlast: number;
  experimentalBlast: number;
  adaptiveContainment: string | number;
  onSelectInstance: (instanceId: string) => void;
  selectedInstanceId?: string | null;
}

export const InstanceCards: React.FC<InstanceCardsProps> = ({
  baselineAvail,
  adaptiveAvail,
  hardenedAvail,
  experimentalAvail,
  baselineBlast,
  adaptiveBlast,
  hardenedBlast,
  experimentalBlast,
  adaptiveContainment,
  onSelectInstance,
  selectedInstanceId
}) => {
  const instances = [
    {
      id: 'env_a_baseline',
      title: 'Env A: Baseline',
      subtitle: 'Fixed Permissive Static Rules',
      badge: 'FIXED POLICY',
      badgeClass: 'bg-slate-200 text-slate-800',
      availability: baselineAvail,
      blastRadius: baselineBlast,
      containment: 'UNCONTAINED (Breach)',
      status: 'BREACH',
      statusClass: 'bg-red-50 text-[#dc2626] border-red-200',
      protocolSummary: 'Static L1/L4 filters. No runtime protocol adaptation.',
      dynamicStatus: 'Static Rules · Lateral Breach to Database',
      borderClass: 'border-slate-200 hover:border-red-300',
      accentColor: '#1e293b',
      isAdaptive: false
    },
    {
      id: 'env_b_adaptive',
      title: 'Env B: Adaptive',
      subtitle: 'Dynamic Defensive Policy Stack + PPO',
      badge: 'DDPS + PPO ACTIVE',
      badgeClass: 'bg-[#dc2626] text-white',
      availability: adaptiveAvail,
      blastRadius: adaptiveBlast,
      containment: typeof adaptiveContainment === 'number' ? `${adaptiveContainment.toFixed(1)}s` : adaptiveContainment,
      status: 'CONTAINED',
      statusClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      protocolSummary: 'Live dynamic modulation across L1-L7 protocols.',
      dynamicStatus: 'Token-Bucket Throttling · L2 CI Quarantine Enforced',
      borderClass: 'border-[#dc2626] shadow-sm ring-1 ring-red-400 bg-red-50/20',
      accentColor: '#dc2626',
      isAdaptive: true
    },
    {
      id: 'env_c_hardened',
      title: 'Env C: Hardened',
      subtitle: 'Strict Static Zero-Trust Rules',
      badge: 'STRICT ZERO-TRUST',
      badgeClass: 'bg-slate-800 text-white',
      availability: hardenedAvail,
      blastRadius: hardenedBlast,
      containment: '0.0s',
      status: 'CONTAINED',
      statusClass: 'bg-slate-100 text-slate-700 border-slate-200',
      protocolSummary: 'Pre-clamped ingress quotas & strict ACLs across all layers.',
      dynamicStatus: 'High False Positives · Static Defense Overhead',
      borderClass: 'border-slate-200 hover:border-slate-400',
      accentColor: '#94a3b8',
      isAdaptive: false
    },
    {
      id: 'env_d_experimental',
      title: 'Env D: Experimental',
      subtitle: 'Heuristic & Alternative RL Agent',
      badge: 'AI TUNING',
      badgeClass: 'bg-amber-100 text-amber-800',
      availability: experimentalAvail,
      blastRadius: experimentalBlast,
      containment: '6.0s',
      status: 'CONTAINED',
      statusClass: 'bg-amber-50 text-amber-700 border-amber-200',
      protocolSummary: 'Autonomous trial-and-error parameter search.',
      dynamicStatus: 'Policy Churn Oscillations · Active Exploration',
      borderClass: 'border-slate-200 hover:border-amber-300',
      accentColor: '#cbd5e1',
      isAdaptive: false
    }
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#dc2626]" />
            Parallel Simulation Instances (Click any card to inspect live protocol adaptation)
          </h2>
          <p className="text-[11px] text-slate-500">
            Four isolated execution domains running identical attack seeds in real-time
          </p>
        </div>
        <span className="text-[11px] font-semibold text-slate-400">
          Click instance to inspect ↗
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {instances.map((inst) => {
          const isSelected = selectedInstanceId === inst.id;

          return (
            <div
              key={inst.id}
              onClick={() => onSelectInstance(inst.id)}
              className={`bg-white border rounded-lg p-5 flex flex-col justify-between cursor-pointer transition-all hover:shadow-md ${
                inst.borderClass
              } ${isSelected ? 'ring-2 ring-[#dc2626]' : ''}`}
            >
              <div>
                {/* Header & Badges */}
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded tracking-wide uppercase ${inst.badgeClass}`}>
                      {inst.badge}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 mt-2 flex items-center gap-1.5">
                      {inst.title}
                      {inst.isAdaptive && <CheckCircle2 className="w-3.5 h-3.5 text-[#dc2626]" />}
                    </h3>
                  </div>
                  <ArrowUpRight className="w-4 h-4 text-slate-400 hover:text-slate-700" />
                </div>

                <div className="text-[11px] text-slate-500 mb-3">{inst.subtitle}</div>

                {/* Primary Availability Bar */}
                <div className="mb-3">
                  <div className="flex justify-between items-baseline mb-1">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Availability</span>
                    <span className={`text-base font-extrabold font-mono ${
                      inst.isAdaptive ? 'text-[#dc2626]' : 'text-slate-900'
                    }`}>
                      {inst.availability.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div 
                      className="h-full transition-all duration-500"
                      style={{ 
                        width: `${Math.min(100, Math.max(5, inst.availability))}%`,
                        backgroundColor: inst.accentColor 
                      }}
                    />
                  </div>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 gap-2 text-xs py-2 border-y border-slate-100 font-mono">
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase block font-sans">Blast Radius</span>
                    <span className="font-bold text-slate-800">{inst.blastRadius.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase block font-sans">MTTC</span>
                    <span className={`font-bold text-[10px] ${inst.status === 'BREACH' ? 'text-[#dc2626]' : 'text-slate-800'}`}>
                      {inst.containment}
                    </span>
                  </div>
                </div>

                {/* Live Dynamic Protocol State */}
                <div className="mt-3 p-2 bg-slate-50 border border-slate-100 rounded text-[10px] text-slate-600 leading-snug">
                  <div className="font-bold text-slate-800 flex items-center gap-1 mb-0.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${inst.isAdaptive ? 'bg-[#dc2626] animate-pulse' : 'bg-slate-400'}`} />
                    Live Protocol Status:
                  </div>
                  <div className="text-slate-500">{inst.dynamicStatus}</div>
                </div>
              </div>

              {/* Bottom Click Hint */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] font-semibold text-[#dc2626]">
                <span>Inspect Protocol Simulation</span>
                <span>↗</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

