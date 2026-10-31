import React from 'react';
import { Play, Square, Target, ChevronDown } from 'lucide-react';

interface HeaderProps {
  isRunning: boolean;
  onRunSimulation: () => void;
  onStopSimulation: () => void;
  selectedScenario: string;
  onSelectScenario: (scenario: string) => void;
  selectedEnvironment?: string;
  onSelectEnvironment?: (env: string) => void;
  step?: number;
  episode?: number;
}

export const Header: React.FC<HeaderProps> = ({
  isRunning,
  onRunSimulation,
  onStopSimulation,
  selectedScenario,
  onSelectScenario,
  selectedEnvironment = 'all',
  onSelectEnvironment,
  step = 0,
  episode = 1
}) => {
  return (
    <div className="border-b border-slate-200 bg-white px-8 pt-6 pb-5">
      {/* Top Breadcrumb & Status */}
      <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
        <div className="flex items-center gap-1.5 font-medium">
          <span className="text-slate-400">localhost</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-700">Overview</span>
        </div>
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200/80 px-2.5 py-1 rounded-full text-[11px] font-semibold text-slate-700">
          <Target className="w-3.5 h-3.5 text-[#dc2626]" />
          <span>Black Sky CI/CD benchmark</span>
          {isRunning && (
            <span className="flex items-center gap-1 text-[#dc2626] font-bold">
              <span className="w-2 h-2 rounded-full bg-[#dc2626] animate-ping" />
              Ep {episode} · T+{step}s
            </span>
          )}
        </div>
      </div>

      {/* Main Title & Action Button */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Defence overview</h1>
          <p className="text-xs text-slate-500 mt-1">Adaptive multi-layer network defence simulator</p>
        </div>

        <div>
          {isRunning ? (
            <button
              onClick={onStopSimulation}
              className="flex items-center gap-2 bg-rose-700 hover:bg-rose-800 text-white px-4 py-2 rounded-md text-xs font-semibold shadow-xs transition-all"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              <span>Stop simulation</span>
            </button>
          ) : (
            <button
              onClick={onRunSimulation}
              className="flex items-center gap-2 bg-[#dc2626] hover:bg-[#b91c1c] text-white px-4 py-2 rounded-md text-xs font-semibold shadow-xs transition-all cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Run simulation</span>
            </button>
          )}
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex items-end justify-between mt-6 pt-4 border-t border-slate-100">
        <div className="flex items-center gap-4">
          {/* ENVIRONMENT */}
          <div>
            <label className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block mb-1">
              ENVIRONMENT
            </label>
            <select
              value={selectedEnvironment}
              onChange={(e) => onSelectEnvironment && onSelectEnvironment(e.target.value)}
              className="border border-slate-200 bg-white px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:border-slate-300 cursor-pointer min-w-[160px] outline-none"
            >
              <option value="all">All environments</option>
              <option value="env_a_baseline">Env A (Baseline)</option>
              <option value="env_b_adaptive">Env B (Adaptive)</option>
              <option value="env_c_hardened">Env C (Hardened)</option>
              <option value="env_d_experimental">Env D (Experimental)</option>
            </select>
          </div>

          {/* ATTACK SCENARIO */}
          <div>
            <label className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block mb-1">
              ATTACK SCENARIO
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => onSelectScenario(e.target.value)}
              className="border border-slate-200 bg-white px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:border-slate-300 cursor-pointer min-w-[160px] outline-none"
            >
              <option value="black_sky">Black Sky CI/CD</option>
              <option value="held_out_evaluation">Held-out WAF & Exfil</option>
            </select>
          </div>

          {/* POLICY FOCUS */}
          <div>
            <label className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block mb-1">
              POLICY FOCUS
            </label>
            <div className="flex items-center gap-2 border border-slate-200 bg-white px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 hover:border-slate-300 cursor-pointer min-w-[180px] justify-between">
              <span>Adaptive - DDPS + PPO</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </div>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 font-medium">
          4 environments / identical attack seeds
        </div>
      </div>
    </div>
  );
};
