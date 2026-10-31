import React from 'react';
import { Shield, ShieldAlert, CheckCircle, Sliders, Lock, AlertTriangle } from 'lucide-react';
import { EnforcedPolicy } from '../types';

interface PolicyStackViewProps {
  enforcedPolicy?: EnforcedPolicy;
}

export const PolicyStackView: React.FC<PolicyStackViewProps> = ({
  enforcedPolicy = {
    edge_rate_limit_level: 2,
    connection_limit_level: 2,
    app_quota_level: 1,
    auth_throttle_level: 2,
    app_concurrency_level: 1,
    segmentation_mode: 2,
    egress_limit_level: 1,
    workload_priority_level: 2,
  }
}) => {
  const controls = [
    { key: 'edge_rate_limit_level', name: 'Edge Rate Limit', desc: 'Ingress packet token-bucket refill rate', value: enforcedPolicy.edge_rate_limit_level },
    { key: 'connection_limit_level', name: 'Connection Ceiling', desc: 'Max concurrent TCP sessions per source IP', value: enforcedPolicy.connection_limit_level },
    { key: 'app_quota_level', name: 'App WAF Quota', desc: 'L7 proof-of-work challenge and route rate limit', value: enforcedPolicy.app_quota_level },
    { key: 'auth_throttle_level', name: 'Auth Throttling', desc: 'Authentication lockout and bcrypt compute limit', value: enforcedPolicy.auth_throttle_level },
    { key: 'app_concurrency_level', name: 'Worker Pool Concurrency', desc: 'Concurrency ceiling on microservice thread pool', value: enforcedPolicy.app_concurrency_level },
    { key: 'segmentation_mode', name: 'East-West Microsegmentation', desc: '0=Default, 1=Strict ACL, 2=Quarantine CI Runner', value: enforcedPolicy.segmentation_mode },
    { key: 'egress_limit_level', name: 'Data Egress Limit', desc: 'Ceiling on sensitive database egress bandwidth', value: enforcedPolicy.egress_limit_level },
    { key: 'workload_priority_level', name: 'SecOps Workload Priority', desc: 'CI/CD runner quota reservation for SecOps tasks', value: enforcedPolicy.workload_priority_level },
  ];

  const levelLabels = ['0: Baseline', '1: Moderate', '2: Strict'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Dynamic Defensive Policy Stack (DDPS)</h2>
          <p className="text-xs text-slate-500 mt-0.5">Continuous multi-layer control modulation with hard security invariants (Ω)</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold px-3 py-1 bg-red-100 text-[#dc2626] rounded flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5" />
            Hard Invariants Ω Enforced
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {controls.map((ctrl) => (
          <div key={ctrl.key} className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-900">{ctrl.name}</span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                ctrl.value === 2 ? 'bg-[#dc2626] text-white' : (ctrl.value === 1 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700')
              }`}>
                {levelLabels[ctrl.value]}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">{ctrl.desc}</p>

            {/* Level Selector Visualizer */}
            <div className="grid grid-cols-3 gap-2">
              {[0, 1, 2].map((lvl) => {
                const isActive = ctrl.value === lvl;
                return (
                  <div
                    key={lvl}
                    className={`text-center py-1.5 rounded text-[11px] font-semibold border transition-all ${
                      isActive 
                        ? (lvl === 2 ? 'bg-[#dc2626] text-white border-[#dc2626]' : 'bg-slate-800 text-white border-slate-800')
                        : 'bg-slate-50 text-slate-400 border-slate-200'
                    }`}
                  >
                    Level {lvl}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Security Invariants Card */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-[#dc2626]" />
          Mandatory Security Invariants (Omega Invariant Pipeline)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
          <div className="flex items-start gap-2.5 p-3 rounded bg-slate-50 border border-slate-100">
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-800">Ω1 &amp; Ω2: Zero Auth Bypass.</span>
              <p className="text-[11px] text-slate-500 mt-0.5">Authentication &amp; RBAC checks are never relaxed regardless of ingress load.</p>
            </div>
          </div>
          <div className="flex items-start gap-2.5 p-3 rounded bg-slate-50 border border-slate-100">
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-800">Ω3: Isolation Boundary.</span>
              <p className="text-[11px] text-slate-500 mt-0.5">Direct CI runner communication to database:5432 remains unconditionally blocked.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

