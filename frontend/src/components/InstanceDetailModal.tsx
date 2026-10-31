import React, { useState } from 'react';
import { 
  X, 
  Shield, 
  ShieldAlert, 
  Radio, 
  Lock, 
  Network, 
  Database, 
  Server, 
  Globe, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import { EnforcedPolicy } from '../types';

interface InstanceDetailModalProps {
  instanceId: string;
  onClose: () => void;
  availability: number;
  blastRadius: number;
  containment: string | number;
  rdi: number;
  simTime: number;
  step: number;
  enforcedPolicy?: EnforcedPolicy;
}

export const InstanceDetailModal: React.FC<InstanceDetailModalProps> = ({
  instanceId,
  onClose,
  availability,
  blastRadius,
  containment,
  rdi,
  simTime,
  step,
  enforcedPolicy
}) => {
  const [activeTab, setActiveTab] = useState<'protocols' | 'topology' | 'timeline' | 'invariants'>('protocols');

  // Instance profile metadata
  const profiles: Record<string, {
    title: string;
    profileName: string;
    description: string;
    port: string;
    engine: string;
    isAdaptive: boolean;
    isBreached: boolean;
  }> = {
    env_a_baseline: {
      title: 'Environment A: Baseline (Fixed Permissive)',
      profileName: 'Static Conventional Policy',
      description: 'Conventional static perimeter with fixed rules. Lacks runtime attack-aware modulation or automated east-west microsegmentation.',
      port: '8001',
      engine: 'Fixed Static Rules Engine',
      isAdaptive: false,
      isBreached: true
    },
    env_b_adaptive: {
      title: 'Environment B: Adaptive (DDPS + Shared PPO)',
      profileName: 'Dynamic Defensive Policy Stack + Shared RL Policy',
      description: 'Continuously adapts multi-layer defensive priorities in real-time under attack telemetry while deterministically enforcing security invariants (Ω).',
      port: '8002',
      engine: 'DDPS Validator + PPO Neural Policy',
      isAdaptive: true,
      isBreached: false
    },
    env_c_hardened: {
      title: 'Environment C: Hardened (Strict Zero-Trust)',
      profileName: 'Static Strict Zero-Trust Baseline',
      description: 'Maximum security controls pre-configured statically across all layers. Eliminates breaches but induces high operational friction and false positive drops.',
      port: '8003',
      engine: 'Static Hardened ACLs',
      isAdaptive: false,
      isBreached: false
    },
    env_d_experimental: {
      title: 'Environment D: Experimental (Alternative RL Agent)',
      profileName: 'Heuristic Tuning & Novel RL Agent',
      description: 'Autonomous exploration testing boundary conditions and novel action transitions across concurrent incident sequences.',
      port: '8004',
      engine: 'Experimental RL Policy Exploration',
      isAdaptive: false,
      isBreached: false
    }
  };

  const currentProfile = profiles[instanceId] || profiles.env_b_adaptive;

  // Protocol Stack Modulation Breakdown
  const protocolStack = [
    {
      layer: 'L1/L2 Edge Ingress',
      protocol: 'TCP SYN Flood Filter & Token Bucket Rate Limiter',
      baselineLevel: 'Level 0 (Unbounded 10,000 rps, no token throttling)',
      currentLevel: instanceId === 'env_b_adaptive' 
        ? 'Level 2 (Strict Token Bucket, 0.88 drop ratio on malicious SYN)' 
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Pre-clamped Strict)' : 'Level 0 (Disabled)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Triggered dynamically at T+15s by volumetric edge flood surge (T1499). DDPS throttled token refill rate, shielding downstream gateway from packet starvation.'
        : (instanceId === 'env_a_baseline' ? 'NO ADAPTATION. Edge gateway CPU saturated to 100%, causing 55% legitimate packet drops.' : 'Static Level 2 pre-configured.'),
      status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'ADAPTED'
    },
    {
      layer: 'L3/L4 Network Transport',
      protocol: 'TCP Session Pool Governor & iptables Conntrack',
      baselineLevel: 'Level 0 (Unlimited concurrent TCP sessions per IP)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 2 (Strict connection limit per source CIDR)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Strict)' : 'Level 0 (Permissive)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Dynamically limits maximum open sockets per source IP, preventing kernel socket descriptor exhaustion during distributed attack waves.'
        : (instanceId === 'env_a_baseline' ? 'NO ADAPTATION. Ephemeral socket exhaustion observed.' : 'Static limit enforced.'),
      status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'ADAPTED'
    },
    {
      layer: 'L4 Identity & Auth',
      protocol: 'JWT Bearer Authentication & Bcrypt Compute Limiter',
      baselineLevel: 'Level 0 (No lockout threshold, 100% compute load under flood)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 2 (Adaptive auth throttling & lockout circuit breaker)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Strict)' : 'Level 0 (Unthrottled)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Triggered dynamically at T+30s by credential stuffing flood (T1110). Bcrypt compute backpressure engaged, lowering auth response latency from 1200ms to 24ms.'
        : (instanceId === 'env_a_baseline' ? 'NO ADAPTATION. Bcrypt thread starvation caused cascaded authentication timeouts.' : 'Static throttle applied.'),
      status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'ADAPTED'
    },
    {
      layer: 'L5 App Gateway / WAF',
      protocol: 'HTTP/REST Proof-of-Work Challenge & Quotas',
      baselineLevel: 'Level 0 (Pass-through routing, no cryptographic challenge)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 1 (Proof-of-work challenge & route rate limit)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Maximum challenge)' : 'Level 0 (Pass-through)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Applies dynamic computational proof-of-work challenges to unverified ingress clients while fast-tracking authenticated sessions.'
        : (instanceId === 'env_a_baseline' ? 'NO ADAPTATION. Unfiltered requests reached internal thread pools.' : 'Static challenge on all requests.'),
      status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'ADAPTED'
    },
    {
      layer: 'L5 Workload Priority',
      protocol: 'Microservice Worker Pool & SecOps Queue Reservation',
      baselineLevel: 'Level 0 (FIFO shared queue, thread pool starvation under flood)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 2 (SecOps thread quota reserved & PR flood throttled)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Strict)' : 'Level 0 (Shared)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Triggered dynamically at T+45s under malicious CI runner PR flood (T1059). Quota reserved for critical internal microservices.'
        : (instanceId === 'env_a_baseline' ? 'NO ADAPTATION. CI runner thread pool exhausted.' : 'Static quota isolation.'),
      status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'ADAPTED'
    },
    {
      layer: 'L6 East-West Network',
      protocol: 'Docker Bridge Microsegmentation & Subnet Isolation',
      baselineLevel: 'Level 0 (Default permissive inter-subnet communication)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 2 (Quarantine CI/CD Subnet - Total Lateral Isolation)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Permanent Quarantine)' : 'Level 0 (Permissive)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'TRIGGERED AT T+60s: Rogue internal port scan detected from ci_runner (T1046). DDPS immediately enforced Mode 2 quarantine. Link ci_runner -> database dynamically severed in <0.1s! Zero lateral breach.'
        : (instanceId === 'env_a_baseline' ? 'CRITICAL FAILURE: No automated microsegmentation. Rogue runner successfully pivoted laterally to internal database, causing complete data compromise.' : 'Permanent isolation (runner cannot communicate).'),
      status: instanceId === 'env_a_baseline' ? 'COMPROMISED' : 'PROTECTED'
    },
    {
      layer: 'L7 Database Storage',
      protocol: 'PostgreSQL Wire Protocol & Egress Bandwidth Governor',
      baselineLevel: 'Level 0 (Uncapped database egress rate)',
      currentLevel: instanceId === 'env_b_adaptive'
        ? 'Level 1 (Strict data egress ceiling & query inspection)'
        : (instanceId === 'env_c_hardened' ? 'Level 2 (Strict egress)' : 'Level 0 (Unrestricted)'),
      dynamicChange: instanceId === 'env_b_adaptive'
        ? 'Egress bandwidth ceiling prevents unauthorized data dumping even during internal reconnaissance probes.'
        : (instanceId === 'env_a_baseline' ? 'BREACHED: Database accessed and compromised by lateral scan.' : 'Static egress limits maintained.'),
      status: instanceId === 'env_a_baseline' ? 'COMPROMISED' : 'PROTECTED'
    }
  ];

  // Microservice Topology nodes for this instance
  const instanceNodes = [
    { id: 'edge_gateway', name: 'Edge Gateway (L1)', status: instanceId === 'env_a_baseline' ? 'SEVERELY_DEGRADED' : 'HEALTHY', latency: instanceId === 'env_a_baseline' ? 180 : 18, cpu: instanceId === 'env_a_baseline' ? 0.95 : 0.28, icon: Globe },
    { id: 'app_gateway', name: 'App Gateway / WAF (L3)', status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'HEALTHY', latency: instanceId === 'env_a_baseline' ? 240 : 22, cpu: instanceId === 'env_a_baseline' ? 0.85 : 0.35, icon: Shield },
    { id: 'auth_service', name: 'Identity & Auth (L4)', status: instanceId === 'env_a_baseline' ? 'SEVERELY_DEGRADED' : 'OPERATIONAL', latency: instanceId === 'env_a_baseline' ? 1200 : 42, cpu: instanceId === 'env_a_baseline' ? 0.98 : 0.45, icon: Lock },
    { id: 'admin_service', name: 'Admin Control Plane (L4)', status: 'HEALTHY', latency: 12, cpu: 0.12, icon: Server },
    { id: 'app_service', name: 'Application Microservice (L5)', status: instanceId === 'env_a_baseline' ? 'DEGRADED' : 'HEALTHY', latency: instanceId === 'env_a_baseline' ? 320 : 28, cpu: instanceId === 'env_a_baseline' ? 0.78 : 0.38, icon: Cpu },
    { id: 'ci_runner', name: 'CI/CD Runner Pool (L5)', status: instanceId === 'env_a_baseline' ? 'COMPROMISED' : 'ISOLATED', latency: 140, cpu: 0.90, icon: Network, isIsolated: instanceId !== 'env_a_baseline' },
    { id: 'internal_service', name: 'Internal Service Bus (L6)', status: 'HEALTHY', latency: 15, cpu: 0.20, icon: Server },
    { id: 'database', name: 'Protected Database (L7)', status: instanceId === 'env_a_baseline' ? 'COMPROMISED' : 'HEALTHY', latency: instanceId === 'env_a_baseline' ? 950 : 14, cpu: 0.25, icon: Database, isCompromised: instanceId === 'env_a_baseline' },
  ];

  // Timeline events for this instance
  const timelineEvents = [
    {
      time: 'T+00s',
      title: 'Quiescent Baseline Normal Traffic',
      protocolChange: 'Baseline telemetry active (100 req/sec nominal). All systems healthy.',
      type: 'info'
    },
    {
      time: 'T+15s',
      title: 'Incident 1: Volumetric Edge SYN Flood (T1499)',
      protocolChange: instanceId === 'env_b_adaptive'
        ? 'DYNAMIC ADAPTATION: Edge token bucket rate limit elevated 0 -> 1 -> 2. Ingress throttled dynamically.'
        : (instanceId === 'env_a_baseline' ? 'STATIC FAILURE: No rule change. Edge queue saturated, packet drop rate exceeds 50%.' : 'Pre-configured static rate limits absorbed surge.'),
      type: instanceId === 'env_a_baseline' ? 'danger' : 'success'
    },
    {
      time: 'T+30s',
      title: 'Incident 2: Auth Credential Stuffing & Hash Starvation (T1110)',
      protocolChange: instanceId === 'env_b_adaptive'
        ? 'DYNAMIC ADAPTATION: Auth throttle level escalated 0 -> 2. Bcrypt compute lockout circuit breaker engaged.'
        : (instanceId === 'env_a_baseline' ? 'STATIC FAILURE: No rate throttling. Bcrypt hashing compute exhaustion causes auth latency >1200ms.' : 'Static auth throttle enforced.'),
      type: instanceId === 'env_a_baseline' ? 'danger' : 'success'
    },
    {
      time: 'T+45s',
      title: 'Incident 3: CI/CD Runner Thread Pool Exhaustion (T1059)',
      protocolChange: instanceId === 'env_b_adaptive'
        ? 'DYNAMIC ADAPTATION: Workload priority level set to 2. SecOps compute quota protected from rogue PR flood.'
        : (instanceId === 'env_a_baseline' ? 'STATIC FAILURE: Thread pool starved. Legitimate build jobs blocked.' : 'Static queue isolation.'),
      type: instanceId === 'env_a_baseline' ? 'danger' : 'success'
    },
    {
      time: 'T+60s',
      title: 'Incident 4: Rogue CI Runner Lateral Port Scan to Database (T1046)',
      protocolChange: instanceId === 'env_b_adaptive'
        ? 'CRITICAL CONTAINMENT: DDPS instantly enforced segmentation mode 2 (Subnet Quarantine). Direct link ci_runner -> database severed! Database preserved.'
        : (instanceId === 'env_a_baseline' ? 'CRITICAL BREACH: Inter-subnet routing permitted connection. Lateral movement reached database:5432! Complete compromise.' : 'Permanent isolation blocked scan.'),
      type: instanceId === 'env_a_baseline' ? 'danger' : 'success'
    },
    {
      time: 'T+90s',
      title: 'Incident Recovery Phase & Policy Hysteresis Evaluation',
      protocolChange: instanceId === 'env_b_adaptive'
        ? 'HYSTERESIS CHECK: DDPS cooldown timer validated. Controlled relaxation of rate limits without thrashing.'
        : (instanceId === 'env_a_baseline' ? 'UNRECOVERED: Cascaded degradation persists. Database remains compromised.' : 'Static policies unchanged.'),
      type: instanceId === 'env_a_baseline' ? 'danger' : 'info'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-xs p-4 sm:p-6 overflow-y-auto">
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header Bar */}
        <div className="p-6 border-b border-slate-200 bg-slate-50 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded tracking-wide uppercase ${
                currentProfile.isBreached 
                  ? 'bg-red-100 text-[#dc2626] border border-red-200' 
                  : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
              }`}>
                {currentProfile.isBreached ? 'BREACHED / UNCONTAINED' : 'CONTAINED & PROTECTED'}
              </span>
              <span className="text-[10px] font-mono text-slate-500 font-semibold">
                Worker Port: {currentProfile.port} · ID: {instanceId}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">{currentProfile.title}</h2>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">{currentProfile.description}</p>
          </div>

          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full border border-slate-200 bg-white hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Live Metrics Quickstrip */}
        <div className="px-6 py-3 bg-white border-b border-slate-100 grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
          <div className="p-2 rounded bg-slate-50 border border-slate-100">
            <span className="text-[9px] uppercase font-bold text-slate-400 block font-sans">Availability</span>
            <span className={`text-base font-extrabold ${
              currentProfile.isAdaptive ? 'text-[#dc2626]' : (currentProfile.isBreached ? 'text-rose-600' : 'text-slate-900')
            }`}>
              {availability.toFixed(1)}%
            </span>
          </div>
          <div className="p-2 rounded bg-slate-50 border border-slate-100">
            <span className="text-[9px] uppercase font-bold text-slate-400 block font-sans">Blast Radius</span>
            <span className="text-base font-extrabold text-slate-800">{blastRadius.toFixed(2)}</span>
          </div>
          <div className="p-2 rounded bg-slate-50 border border-slate-100">
            <span className="text-[9px] uppercase font-bold text-slate-400 block font-sans">MTTC Containment</span>
            <span className={`text-xs font-extrabold block mt-1 ${currentProfile.isBreached ? 'text-[#dc2626]' : 'text-emerald-700'}`}>
              {typeof containment === 'number' ? `${containment.toFixed(1)}s` : containment}
            </span>
          </div>
          <div className="p-2 rounded bg-slate-50 border border-slate-100">
            <span className="text-[9px] uppercase font-bold text-slate-400 block font-sans">RDI Degradation</span>
            <span className="text-base font-extrabold text-slate-800">{rdi.toFixed(1)}</span>
          </div>
          <div className="p-2 rounded bg-slate-50 border border-slate-100">
            <span className="text-[9px] uppercase font-bold text-slate-400 block font-sans">Sim Clock</span>
            <span className="text-base font-extrabold text-slate-800">T+{simTime}s</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="px-6 pt-3 border-b border-slate-200 bg-white flex items-center gap-6 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('protocols')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'protocols' 
                ? 'border-[#dc2626] text-[#dc2626]' 
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Live Protocol Modulation</span>
          </button>

          <button
            onClick={() => setActiveTab('topology')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'topology' 
                ? 'border-[#dc2626] text-[#dc2626]' 
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            <span>Instance Microservice Topology</span>
          </button>

          <button
            onClick={() => setActiveTab('timeline')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'timeline' 
                ? 'border-[#dc2626] text-[#dc2626]' 
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Dynamic Protocol Timeline</span>
          </button>

          <button
            onClick={() => setActiveTab('invariants')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'invariants' 
                ? 'border-[#dc2626] text-[#dc2626]' 
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Security Invariants (Ω)</span>
          </button>
        </div>

        {/* Tab Content Area */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 bg-[#fcfcfd]">
          {/* TAB 1: Live Protocol Modulation */}
          {activeTab === 'protocols' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    OSI Layer Protocols &amp; Live Dynamic Modulation
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    How protocols and control policies are dynamically adjusted during concurrent attacks
                  </p>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">
                  Control Engine: {currentProfile.engine}
                </span>
              </div>

              <div className="space-y-3">
                {protocolStack.map((item, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                          {item.layer}
                        </span>
                        <span className="text-xs font-bold text-slate-900">{item.protocol}</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded tracking-wide uppercase ${
                        item.status === 'COMPROMISED' ? 'bg-red-50 text-[#dc2626] border border-red-200' :
                        (item.status === 'DEGRADED' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-emerald-50 text-emerald-700 border border-emerald-200')
                      }`}>
                        {item.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mb-2.5">
                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                        <span className="text-[9px] uppercase font-bold text-slate-400 block mb-0.5 font-sans">
                          Baseline Protocol Configuration
                        </span>
                        <span className="font-mono text-slate-700 text-[11px]">{item.baselineLevel}</span>
                      </div>
                      <div className="p-2.5 rounded bg-red-50/40 border border-red-100">
                        <span className="text-[9px] uppercase font-bold text-[#dc2626] block mb-0.5 font-sans">
                          Current Enforced Protocol State
                        </span>
                        <span className="font-mono text-slate-900 font-semibold text-[11px]">{item.currentLevel}</span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded bg-slate-50 border border-slate-100/80 text-[11px] text-slate-600 leading-relaxed flex items-start gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-[#dc2626] shrink-0 mt-0.5" />
                      <span>{item.dynamicChange}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: Instance Microservice Topology */}
          {activeTab === 'topology' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Live Node State in {currentProfile.title}
                </h3>
                <p className="text-[11px] text-slate-500">
                  Inspect the physical microservices and quarantine status in this isolated environment
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {instanceNodes.map((node) => {
                  const Icon = node.icon;
                  const isCompromised = node.isCompromised;
                  const isIsolated = node.isIsolated;

                  return (
                    <div 
                      key={node.id} 
                      className={`p-4 rounded-lg border bg-white ${
                        isCompromised ? 'border-red-400 bg-red-50/50 ring-1 ring-red-400' :
                        (isIsolated ? 'border-blue-400 bg-blue-50/30' : 'border-slate-200')
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className={`w-8 h-8 rounded-md flex items-center justify-center ${
                          isCompromised ? 'bg-[#dc2626] text-white' : (isIsolated ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700')
                        }`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          isCompromised ? 'bg-red-100 text-[#dc2626]' :
                          (isIsolated ? 'bg-blue-100 text-blue-700' :
                          (node.status === 'HEALTHY' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'))
                        }`}>
                          {node.status}
                        </span>
                      </div>
                      <div className="text-xs font-bold text-slate-900 truncate mb-1">{node.name}</div>
                      <div className="text-[10px] font-mono text-slate-500 space-y-0.5">
                        <div className="flex justify-between">
                          <span>Latency:</span>
                          <span className={node.latency > 200 ? 'text-[#dc2626] font-bold' : 'text-slate-800'}>{node.latency} ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span>CPU Pressure:</span>
                          <span className="font-semibold text-slate-800">{(node.cpu * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {currentProfile.isBreached && (
                <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-xs text-[#dc2626] leading-relaxed flex items-start gap-2.5">
                  <ShieldAlert className="w-5 h-5 shrink-0 text-[#dc2626]" />
                  <div>
                    <span className="font-bold">CRITICAL BREACH IN BASELINE: </span>
                    Because Environment A relies on static firewall configurations, the rogue CI runner lateral port probe was not dynamically intercepted. Lateral movement reached `database:5432`, resulting in data exfiltration risk and dropping availability to 39.8%.
                  </div>
                </div>
              )}

              {currentProfile.isAdaptive && (
                <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 leading-relaxed flex items-start gap-2.5">
                  <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600" />
                  <div>
                    <span className="font-bold">ADAPTIVE SUCCESS IN ENV B: </span>
                    The DDPS orchestrator detected east-west anomaly telemetry at T+60s and dynamically quarantined the CI runner subnet in under 100 milliseconds. The database remained 100% protected throughout the multi-stage attack.
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Dynamic Protocol Timeline */}
          {activeTab === 'timeline' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Attack Sequence &amp; Dynamic Response Chronology
                </h3>
                <p className="text-[11px] text-slate-500">
                  Step-by-step trace of how this instance reacted to active MITRE ATT&CK incidents
                </p>
              </div>

              <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {timelineEvents.map((evt, i) => (
                  <div key={i} className="relative">
                    <span className={`absolute -left-6 top-1 w-3 h-3 rounded-full border-2 border-white ${
                      evt.type === 'danger' ? 'bg-[#dc2626]' : (evt.type === 'success' ? 'bg-emerald-600' : 'bg-slate-500')
                    }`} />
                    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-900">{evt.title}</span>
                        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                          {evt.time}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed mt-1">
                        {evt.protocolChange}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Security Invariants (Omega) */}
          {activeTab === 'invariants' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Mandatory Security Invariants Audit (Ω)
                </h3>
                <p className="text-[11px] text-slate-500">
                  Non-negotiable security boundaries that the agent is mathematically forbidden from violating
                </p>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-2xs flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900">Ω1 &amp; Ω2: Zero Authentication Bypass.</span>
                    <p className="text-[11px] text-slate-600 mt-0.5">
                      Required authentication and token validation are never disabled regardless of ingress load or CPU saturation. P(AuthBypass) = 0.
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-2xs flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900">Ω3: Isolation Boundary Enforcement.</span>
                    <p className="text-[11px] text-slate-600 mt-0.5">
                      Direct CI/CD runner communication to database:5432 remains unconditionally blocked under all operating regimes.
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-2xs flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900">Ω4 &amp; Ω5: Parameter Interval Ceiling &amp; Egress Guard.</span>
                    <p className="text-[11px] text-slate-600 mt-0.5">
                      Defensive adjustments must strictly stay within approved intervals [0, 2]^8 and database egress cannot exceed safe ceilings.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#dc2626] animate-pulse" />
            <span>Streaming Live Telemetry (WebSocket / Redis PubSub)</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-slate-800 hover:bg-slate-900 text-white font-semibold text-xs transition-colors"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
};

