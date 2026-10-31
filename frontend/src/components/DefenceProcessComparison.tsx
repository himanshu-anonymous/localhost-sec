import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

interface ProcessComparisonProps {
  baselineAvail: number;
  baselineBlast: number;
  adaptiveAvail: number;
  adaptiveBlast: number;
  adaptiveContainment: string | number;
}

export const DefenceProcessComparison: React.FC<ProcessComparisonProps> = ({
  baselineAvail,
  baselineBlast,
  adaptiveAvail,
  adaptiveBlast,
  adaptiveContainment
}) => {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs space-y-4">
      <div>
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          Defence process comparison
        </h2>
        <p className="text-[11px] text-slate-500">
          Static vs. Adaptive DDPS + shared PPO
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Static defence process */}
        <div className="border border-slate-200 rounded-lg p-5 flex flex-col justify-between bg-slate-50/50">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
              <span className="text-xs font-bold text-slate-800">Static defence process</span>
              <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700 tracking-wide">
                FIXED POLICY
              </span>
            </div>

            <ol className="space-y-3 text-xs text-slate-600">
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                  1
                </span>
                <span>Fixed policy is applied before the attack starts.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                  2
                </span>
                <span>Traffic is evaluated against a static allow/deny list.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                  3
                </span>
                <span>No runtime adaptation occurs; the policy does not change.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                  4
                </span>
                <span>Breach or containment depends on the fixed policy state.</span>
              </li>
            </ol>
          </div>

          <div className="mt-5 p-3 rounded-md bg-red-50 border border-red-100 flex items-center gap-2.5 text-xs text-[#dc2626] font-semibold">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>
              Baseline outcome: Breach - {baselineAvail.toFixed(1)}% availability - {baselineBlast.toFixed(2)} blast radius
            </span>
          </div>
        </div>

        {/* Right: Our system's dynamic defence process */}
        <div className="border border-red-200 rounded-lg p-5 flex flex-col justify-between bg-red-50/20">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-red-100">
              <span className="text-xs font-bold text-slate-900">Our system's dynamic defence process</span>
              <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-[#dc2626] text-white tracking-wide">
                ADAPTIVE
              </span>
            </div>

            <ol className="space-y-3 text-xs text-slate-700 font-medium">
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-[#dc2626] text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                  1
                </span>
                <span>Network observations and telemetry inform policy decisions in real-time.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-[#dc2626] text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                  2
                </span>
                <span>DDPS adjusts multi-layer defensive control priorities in real-time.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-[#dc2626] text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                  3
                </span>
                <span>Non-negotiable security invariants Ω are validated before action.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-[#dc2626] text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                  4
                </span>
                <span>Safe defensive actions are applied with feedback from the environment.</span>
              </li>
            </ol>
          </div>

          <div className="mt-5 p-3 rounded-md bg-emerald-50 border border-emerald-100 flex items-center gap-2.5 text-xs text-emerald-800 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              Adaptive outcome: Contained - {adaptiveAvail.toFixed(1)}% availability - {adaptiveBlast.toFixed(2)} blast radius - {typeof adaptiveContainment === 'number' ? `${adaptiveContainment.toFixed(1)}s` : adaptiveContainment} containment
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

