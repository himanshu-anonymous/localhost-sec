import React from 'react';
import { Radio, KeyRound, GitFork } from 'lucide-react';

export const ScenarioAttacks: React.FC = () => {
  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">
          Scenario attacks
        </h2>
        <p className="text-[11px] text-slate-500">
          Simultaneous attack vectors
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Vector 1: Edge DDoS */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs hover:border-slate-300 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <Radio className="w-4 h-4 text-[#dc2626]" />
            <h3 className="text-xs font-bold text-slate-900">Edge DDoS</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Saturates edge ingress with high-volume traffic to degrade availability.
          </p>
        </div>

        {/* Vector 2: Auth Stuffing */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs hover:border-slate-300 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <KeyRound className="w-4 h-4 text-[#dc2626]" />
            <h3 className="text-xs font-bold text-slate-900">Auth Stuffing</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Exhausts authentication endpoints, to slow service response and create denial.
          </p>
        </div>

        {/* Vector 3: Lateral Exploitation */}
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-2xs hover:border-slate-300 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <GitFork className="w-4 h-4 text-[#dc2626]" />
            <h3 className="text-xs font-bold text-slate-900">Lateral Exploitation</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Exploits CI/CD dependencies to move laterally and increase blast radius.
          </p>
        </div>
      </div>
    </div>
  );
};

