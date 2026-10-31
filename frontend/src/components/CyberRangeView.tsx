import React from 'react';
import { Box, CheckCircle2, XCircle, ArrowUpRight, Terminal, RefreshCw } from 'lucide-react';

export const CyberRangeView: React.FC = () => {
  const containers = [
    { id: 'worker-a', name: 'localhost-worker-a', env: 'env_a_baseline', port: '8001', profile: 'Fixed Permissive', healthy: true },
    { id: 'worker-b', name: 'localhost-worker-b', env: 'env_b_adaptive', port: '8002', profile: 'Adaptive DDPS + PPO', healthy: true },
    { id: 'worker-c', name: 'localhost-worker-c', env: 'env_c_hardened', port: '8003', profile: 'Strict Zero-Trust', healthy: true },
    { id: 'worker-d', name: 'localhost-worker-d', env: 'env_d_experimental', port: '8004', profile: 'Heuristic Tuning', healthy: true },
    { id: 'redis', name: 'localhost-redis', env: 'telemetry_broker', port: '6380:6379', profile: 'Pub/Sub Event Broker', healthy: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Docker Cyber-Range Infrastructure</h2>
          <p className="text-xs text-slate-500 mt-0.5">Isolated containerized validation domain (Domain B)</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold px-3 py-1 bg-emerald-100 text-emerald-800 rounded flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Bridge Network: localhost-net (Online)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {containers.map((c) => (
          <div key={c.id} className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Box className="w-4 h-4 text-[#dc2626]" />
                  <span className="font-bold text-xs text-slate-900 font-mono">{c.name}</span>
                </div>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  Running
                </span>
              </div>
              <div className="text-[11px] text-slate-500 mb-1">{c.profile}</div>
              <div className="text-[10px] font-mono text-slate-400">Target: {c.env}</div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">PORT</span>
              <span className="font-semibold text-slate-700">{c.port}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
          Cyber-Range Validation Workflow
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          The containerized validation domain enforces strict human review before deploying trained policy checkpoints to live Docker environments. 
          Actions selected in the fast simulation layer (Domain A) are statically verified against invariant constraints before container emission.
        </p>
      </div>
    </div>
  );
};

