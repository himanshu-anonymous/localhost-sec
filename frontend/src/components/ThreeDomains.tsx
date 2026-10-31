import React from 'react';
import { ArrowUpRight, Shield, Terminal, Sparkles, Cpu, Layers } from 'lucide-react';

export const ThreeDomains: React.FC = () => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          One policy stack. Three isolated domains.
        </h2>
        <div className="text-[11px] font-semibold text-slate-400 tracking-wider">
          Train · Validate · Explain
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Domain A: Fast Simulation */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#dc2626]" />
                <h3 className="text-xs font-bold text-slate-900">Fast simulation</h3>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="text-[10px] font-mono text-slate-400 font-semibold mb-2 uppercase">
              GYMNASIUM / SHARED PPO
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Train adaptive defensive policies at &gt;100Hz in the fast simulation environment.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100">
            <span className="text-[9px] font-mono font-bold text-slate-400 tracking-wider uppercase">
              TRAINING &amp; BENCHMARKING
            </span>
          </div>
        </div>

        {/* Domain B: Container Cyber-Range */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-slate-700" />
                <h3 className="text-xs font-bold text-slate-900">Container cyber-range</h3>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="text-[10px] font-mono text-slate-400 font-semibold mb-2 uppercase">
              DOCKER / PRIVATE NETWORK
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Validate human-approved policy checkpoints inside an isolated private network.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100">
            <span className="text-[9px] font-mono font-bold text-slate-400 tracking-wider uppercase">
              HUMAN APPROVAL REQUIRED
            </span>
          </div>
        </div>

        {/* Domain C: AI Reasoning */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs flex flex-col justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#dc2626]" />
                <h3 className="text-xs font-bold text-slate-900">AI reasoning</h3>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="text-[10px] font-mono text-slate-400 font-semibold mb-2 uppercase">
              GEMMA 4 / OUT-OF-BAND
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Structured explanations and root-cause analysis, separate from the control loop.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100">
            <span className="text-[9px] font-mono font-bold text-slate-400 tracking-wider uppercase">
              EXPLAINING CONTROL
            </span>
          </div>
        </div>
      </div>

      <div className="text-[10px] text-slate-400 font-mono">
        BASTION X / Adaptive multi-layer network defence
      </div>
    </div>
  );
};

