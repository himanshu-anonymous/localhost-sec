import React, { useState } from 'react';
import { Shield, Server, Database, Globe, Network, Cpu, Lock, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { NodeState } from '../types';

interface SimulationsViewProps {
  currentStep: number;
  simTime: number;
  activeIncidents?: string[];
}

export const SimulationsView: React.FC<SimulationsViewProps> = ({
  currentStep,
  simTime,
  activeIncidents = ['T1499', 'T1110']
}) => {
  const [selectedNode, setSelectedNode] = useState<string | null>('edge_gateway');

  const nodes = [
    { id: 'edge_gateway', name: 'Edge Gateway (L1)', layer: 1, type: 'edge', status: 'HEALTHY', cpu: 0.28, mem: 0.32, latency: 18, req: '480 rps', icon: Globe },
    { id: 'app_gateway', name: 'App Gateway / WAF (L3)', layer: 3, type: 'waf', status: 'HEALTHY', cpu: 0.35, mem: 0.40, latency: 24, req: '420 rps', icon: Shield },
    { id: 'auth_service', name: 'Identity & Auth (L4)', layer: 4, type: 'auth', status: 'OPERATIONAL', cpu: 0.45, mem: 0.52, latency: 45, req: '150 rps', icon: Lock },
    { id: 'admin_service', name: 'Admin Control Plane (L4)', layer: 4, type: 'admin', status: 'HEALTHY', cpu: 0.12, mem: 0.22, latency: 12, req: '15 rps', icon: Server },
    { id: 'app_service', name: 'Application Microservice (L5)', layer: 5, type: 'app', status: 'HEALTHY', cpu: 0.38, mem: 0.48, latency: 28, req: '380 rps', icon: Cpu },
    { id: 'ci_runner', name: 'CI/CD Runner Pool (L5)', layer: 5, type: 'runner', status: 'DEGRADED', cpu: 0.88, mem: 0.75, latency: 120, req: '80 rps', icon: Network, isIsolated: true },
    { id: 'internal_service', name: 'Internal Service Bus (L6)', layer: 6, type: 'bus', status: 'HEALTHY', cpu: 0.20, mem: 0.30, latency: 15, req: '210 rps', icon: Server },
    { id: 'database', name: 'Protected Database (L7)', layer: 7, type: 'db', status: 'HEALTHY', cpu: 0.25, mem: 0.60, latency: 14, req: '180 rps', icon: Database },
  ];

  const activeNodeData = nodes.find(n => n.id === selectedNode) || nodes[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Live Network Topology &amp; Attack Simulation</h2>
          <p className="text-xs text-slate-500 mt-0.5">8 canonical microservices across 7 defense layers (Domain A / B Model)</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1 bg-slate-100 rounded text-slate-700">
            Clock: T+{simTime}s (Step {currentStep})
          </span>
          <span className="text-xs font-bold px-3 py-1 bg-red-100 text-[#dc2626] rounded flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#dc2626] animate-pulse" />
            Attack Emulation Active
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Topology Schematic */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-lg p-6 shadow-2xs relative overflow-hidden">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-6 flex justify-between">
            <span>Enterprise Network Perimeter (Deny-by-default allowlist)</span>
            <span className="text-slate-500">Click node to inspect</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 relative z-10">
            {nodes.map((node) => {
              const Icon = node.icon;
              const isSelected = selectedNode === node.id;
              const isIsolated = node.isIsolated;

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    isSelected 
                      ? 'border-[#dc2626] bg-red-50/30 shadow-xs ring-1 ring-red-500' 
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-8 h-8 rounded-md flex items-center justify-center ${
                      isSelected ? 'bg-[#dc2626] text-white' : 'bg-slate-100 text-slate-700'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    {isIsolated ? (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                        ISOLATED
                      </span>
                    ) : (
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                        node.status === 'HEALTHY' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                      }`}>
                        {node.status}
                      </span>
                    )}
                  </div>

                  <div className="font-bold text-xs text-slate-900 mb-1 truncate">{node.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between">
                    <span>CPU: {(node.cpu * 100).toFixed(0)}%</span>
                    <span>{node.latency}ms</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active Flow Legend */}
          <div className="mt-8 pt-4 border-t border-slate-100 flex flex-wrap items-center gap-6 text-[11px] text-slate-500">
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-[#dc2626]" />
              <span>Attacked Path (Ingress / SYN Flood)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-emerald-500" />
              <span>Legitimate Clean Path</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-blue-500 border-dashed border-t" />
              <span>Quarantine Microsegmentation Mode 2</span>
            </div>
          </div>
        </div>

        {/* Selected Node Inspector Drawer */}
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Node Telemetry Inspector</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Layer {activeNodeData.layer}
              </span>
            </div>

            <div className="mb-4">
              <div className="text-base font-bold text-slate-900">{activeNodeData.name}</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">ID: {activeNodeData.id}</div>
            </div>

            <div className="space-y-3.5">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">CPU Pressure</span>
                  <span className="font-mono font-bold text-slate-800">{(activeNodeData.cpu * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className={`h-full ${activeNodeData.cpu > 0.8 ? 'bg-[#dc2626]' : 'bg-slate-700'}`} style={{ width: `${activeNodeData.cpu * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Memory Utilization</span>
                  <span className="font-mono font-bold text-slate-800">{(activeNodeData.mem * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-slate-700 h-full" style={{ width: `${activeNodeData.mem * 100}%` }} />
                </div>
              </div>

              <div className="pt-2 grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Response Latency</div>
                  <div className="text-sm font-bold text-slate-800 font-mono mt-0.5">{activeNodeData.latency} ms</div>
                </div>
                <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Ingress Rate</div>
                  <div className="text-sm font-bold text-slate-800 font-mono mt-0.5">{activeNodeData.req}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-500">
            {activeNodeData.isIsolated ? (
              <span className="text-blue-700 font-semibold flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5" /> Quarantined by DDPS segmentation rule
              </span>
            ) : (
              <span className="text-emerald-700 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Healthy communication path verified
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

