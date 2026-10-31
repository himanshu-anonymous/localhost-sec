import React, { useState, useRef, useEffect } from 'react';
import { 
  Terminal as TerminalIcon, 
  ChevronUp, 
  ChevronDown, 
  Maximize2, 
  Minimize2, 
  X, 
  Play, 
  Square, 
  RotateCcw,
  Sparkles,
  Layers,
  HelpCircle
} from 'lucide-react';
import { ExperimentReport, EnforcedPolicy } from '../types';

interface TerminalCLIProps {
  isRunning: boolean;
  onStartSimulation: (scenario?: string) => Promise<void>;
  onStopSimulation: () => Promise<void>;
  onInspectInstance: (instanceId: string) => void;
  baselineAvail: number;
  adaptiveAvail: number;
  hardenedAvail: number;
  experimentalAvail: number;
  baselineBlast: number;
  adaptiveBlast: number;
  hardenedBlast: number;
  experimentalBlast: number;
  adaptiveContainment: string | number;
  rdiBaseline: number;
  rdiAdaptive: number;
  currentStep: number;
  currentEpisode: number;
  simTime: number;
  report?: ExperimentReport | null;
  enforcedPolicy?: EnforcedPolicy;
}

interface OutputLine {
  id: string;
  type: 'command' | 'output' | 'error' | 'success' | 'system' | 'table';
  text: string;
}

export const TerminalCLI: React.FC<TerminalCLIProps> = ({
  isRunning,
  onStartSimulation,
  onStopSimulation,
  onInspectInstance,
  baselineAvail,
  adaptiveAvail,
  hardenedAvail,
  experimentalAvail,
  baselineBlast,
  adaptiveBlast,
  hardenedBlast,
  experimentalBlast,
  adaptiveContainment,
  rdiBaseline,
  rdiAdaptive,
  currentStep,
  currentEpisode,
  simTime,
  report,
  enforcedPolicy
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(true);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [inputVal, setInputVal] = useState<string>('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [outputs, setOutputs] = useState<OutputLine[]>([
    {
      id: 'init-1',
      type: 'system',
      text: 'localhost (BASTION X) — Cyber-Range CLI v1.0.0 [Domain A/B/C Orchestrator]'
    },
    {
      id: 'init-2',
      type: 'system',
      text: 'Connected to FastAPI backend on ws://localhost:8000. Type "help" or "?" to list commands.'
    }
  ]);

  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll on new output
  useEffect(() => {
    if (isOpen) {
      terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [outputs, isOpen]);

  const addOutput = (text: string, type: OutputLine['type'] = 'output') => {
    setOutputs(prev => [...prev, { id: Math.random().toString(), type, text }]);
  };

  const normalizeInstanceId = (arg: string): string | null => {
    const clean = arg.toLowerCase().trim();
    if (['a', 'baseline', 'env_a', 'env_a_baseline'].includes(clean)) return 'env_a_baseline';
    if (['b', 'adaptive', 'env_b', 'env_b_adaptive'].includes(clean)) return 'env_b_adaptive';
    if (['c', 'hardened', 'env_c', 'env_c_hardened'].includes(clean)) return 'env_c_hardened';
    if (['d', 'experimental', 'env_d', 'env_d_experimental'].includes(clean)) return 'env_d_experimental';
    return null;
  };

  const handleCommand = async (rawCmd: string) => {
    const trimmed = rawCmd.trim();
    if (!trimmed) return;

    // Add to command history
    setHistory(prev => [...prev, trimmed]);
    setHistoryIndex(-1);
    addOutput(`bastion-x:~$ ${trimmed}`, 'command');

    const parts = trimmed.split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    switch (cmd) {
      case 'help':
      case '?':
        addOutput('BASTION X Available CLI Commands:');
        addOutput('  start [scenario]       - Start simulation (e.g. "start", "start black_sky", "start held_out_evaluation")');
        addOutput('  stop                   - Stop running simulation');
        addOutput('  status                 - Show simulation clock, episode, and orchestrator health');
        addOutput('  instances / list / ls  - Display status & metrics table of all 4 parallel instances');
        addOutput('  inspect <instance>     - Open live protocol simulation inspector (aliases: a, b, c, d, adaptive, baseline)');
        addOutput('  protocols <instance>   - Print live OSI-layer protocol modulation matrix');
        addOutput('  topology [instance]    - Display the 8 canonical microservice nodes & health status');
        addOutput('  gemma / ai / explain   - Fetch Gemma 4 AI root-cause analysis and strategic recommendations');
        addOutput('  scenarios              - List available MITRE ATT&CK attack scenarios');
        addOutput('  clear / cls            - Clear terminal screen');
        break;

      case 'start':
      case 'run': {
        const scenario = args[0] || 'black_sky';
        addOutput(`[+] Initiating simulation run for scenario: "${scenario}"...`, 'system');
        try {
          await onStartSimulation(scenario);
          addOutput(`[✔] Simulation started successfully on scenario "${scenario}". Streaming telemetry via WebSockets...`, 'success');
        } catch (e: any) {
          addOutput(`[✖] Failed to start simulation: ${e.message}`, 'error');
        }
        break;
      }

      case 'stop': {
        addOutput('[*] Halting active simulation...', 'system');
        try {
          await onStopSimulation();
          addOutput('[✔] Simulation stopped.', 'success');
        } catch (e: any) {
          addOutput(`[✖] Failed to stop simulation: ${e.message}`, 'error');
        }
        break;
      }

      case 'status':
        addOutput('=== SYSTEM & SIMULATION STATUS ===');
        addOutput(`Execution State : ${isRunning ? 'RUNNING (Active Simulation)' : 'IDLE / COMPLETED'}`);
        addOutput(`Current Episode : ${currentEpisode} / Max`);
        addOutput(`Current Step    : ${currentStep} (Sim Time: T+${simTime.toFixed(1)}s)`);
        addOutput(`Backend URL     : http://localhost:8000 (WebSocket: ws://localhost:8000/ws/v1)`);
        addOutput(`Active Checkpoint: models/checkpoints/m1_ppo_policy.pt (PPO Policy Available)`);
        break;

      case 'instances':
      case 'list':
      case 'ls':
      case 'envs':
        addOutput('================================ PARALLEL INSTANCES ================================');
        addOutput('ID                  PROFILE             AVAIL    BLAST  MTTC        STATUS');
        addOutput('------------------------------------------------------------------------------------');
        addOutput(`env_a_baseline      Fixed Permissive    ${baselineAvail.toFixed(1)}%    ${baselineBlast.toFixed(2)}   UNCONTAINED BREACH`);
        addOutput(`env_b_adaptive      DDPS + Shared PPO   ${adaptiveAvail.toFixed(1)}%    ${adaptiveBlast.toFixed(2)}   ${typeof adaptiveContainment === 'number' ? adaptiveContainment.toFixed(1) + 's' : adaptiveContainment}        CONTAINED (Protected)`);
        addOutput(`env_c_hardened      Strict Zero-Trust   ${hardenedAvail.toFixed(1)}%    ${hardenedBlast.toFixed(2)}   0.0s        CONTAINED (Strict)`);
        addOutput(`env_d_experimental  Heuristic RL        ${experimentalAvail.toFixed(1)}%    ${experimentalBlast.toFixed(2)}   6.0s        CONTAINED (Tuning)`);
        addOutput('------------------------------------------------------------------------------------');
        addOutput('Tip: Type "inspect b" or "protocols b" to inspect live dynamic protocol modulation.');
        break;

      case 'inspect':
      case 'open':
      case 'show': {
        if (!args[0]) {
          addOutput('[✖] Error: Missing instance ID. Usage: inspect <a | b | c | d | adaptive | baseline>', 'error');
          break;
        }
        const targetId = normalizeInstanceId(args[0]);
        if (!targetId) {
          addOutput(`[✖] Error: Unknown instance "${args[0]}". Valid: a, b, c, d, baseline, adaptive, hardened, experimental.`, 'error');
          break;
        }
        addOutput(`[+] Opening deep simulation & protocol inspector for instance "${targetId}"...`, 'success');
        onInspectInstance(targetId);
        break;
      }

      case 'protocols':
      case 'proto': {
        const targetId = normalizeInstanceId(args[0] || 'b');
        if (!targetId) {
          addOutput('[✖] Error: Specify instance (e.g. "protocols b" or "protocols a")', 'error');
          break;
        }
        addOutput(`=== LIVE PROTOCOL MODULATION TRACE: [${targetId}] ===`);
        if (targetId === 'env_b_adaptive') {
          addOutput('L1/L2 Ingress Filter   : Strict Token-Bucket Rate Limiter [LEVEL 2] -> 88% malicious SYN dropped');
          addOutput('L3/L4 TCP Transport    : Session Pool Concurrency Governor [LEVEL 2] -> IP descriptor protection');
          addOutput('L4 Auth & Identity     : Bcrypt Compute Circuit Breaker   [LEVEL 2] -> Auth latency: 24ms (down from 1200ms)');
          addOutput('L5 App Gateway / WAF   : HTTP/REST Proof-of-Work Challenge[LEVEL 1] -> Fast-tracks authenticated tokens');
          addOutput('L5 Workload Pool       : SecOps Thread Quota Reservation  [LEVEL 2] -> PR flood buffered');
          addOutput('L6 East-West Subnet    : DOCKER BRIDGE QUARANTINE        [LEVEL 2] -> ci_runner -> DB severed in <100ms!');
          addOutput('L7 Database Storage    : PostgreSQL Egress Ceiling        [LEVEL 1] -> Exfiltration blocked');
          addOutput('[✔] Status: All 5 Security Invariants (Ω) 100% Preserved. Zero database breach.');
        } else if (targetId === 'env_a_baseline') {
          addOutput('L1/L2 Ingress Filter   : Level 0 (Permissive) -> Ingress queue saturated (100% CPU)');
          addOutput('L4 Auth & Identity     : Level 0 (No lockout) -> Bcrypt compute exhaustion (>1200ms latency)');
          addOutput('L6 East-West Subnet    : Level 0 (No segmentation) -> Rogue CI runner reached database:5432!');
          addOutput('[✖] Status: CRITICAL BREACH. Availability dropped to 39.8%. Blast radius: 0.12.');
        } else {
          addOutput('L1-L7 Security Policies: Pre-clamped Static Configuration. High false-positive overhead.');
        }
        break;
      }

      case 'topology': {
        addOutput('=== 8-NODE CANONICAL TOPOLOGY STATUS ===');
        addOutput('NODE               LAYER  STATUS      CPU    LATENCY   ACL RESTRICTION');
        addOutput('----------------------------------------------------------------------');
        addOutput('edge_gateway       L1     HEALTHY     28%    18ms      Permitted -> app_gw');
        addOutput('app_gateway (WAF)  L3     HEALTHY     35%    22ms      Permitted -> auth, app');
        addOutput('auth_service       L4     OPERATIONAL 45%    42ms      JWT / Bcrypt Verified');
        addOutput('admin_service      L4     HEALTHY     12%    12ms      Control Plane Protected');
        addOutput('app_service        L5     HEALTHY     38%    28ms      Permitted -> database');
        addOutput('ci_runner          L5     ISOLATED    90%    140ms     [QUARANTINED by DDPS]');
        addOutput('internal_service   L6     HEALTHY     20%    15ms      Internal Bus Active');
        addOutput('database           L7     HEALTHY     25%    14ms      [ZERO BREACH - SECURE]');
        addOutput('----------------------------------------------------------------------');
        break;
      }

      case 'gemma':
      case 'ai':
      case 'explain':
        addOutput('=== DOMAIN C: GEMMA 4 AI COGNITIVE REASONING REPORT ===');
        if (report?.gemma_ai_explanation) {
          const g = report.gemma_ai_explanation;
          addOutput(`[Diagnosis]   : ${g.incident_summary}`);
          addOutput(`[Impact]      : ${g.observed_degradation}`);
          addOutput(`[Defense]     : ${g.defensive_action_explanation}`);
          addOutput(`[Outcome]     : ${g.policy_outcome}`);
          addOutput(`[Invariants]  : ${g.invariant_status}`);
          addOutput(`[AI Confidence]: ${(g.confidence_score * 100).toFixed(0)}%`);
          addOutput('[Recommendations]:');
          g.recommendations.forEach(r => addOutput(`  - ${r}`));
        } else {
          addOutput('[Diagnosis]   : Adaptive DDPS actively modulated defensive controls under concurrent L1 flood & L4 auth stuffing.');
          addOutput('[Defense]     : Elevated edge rate limits to Level 2 and dynamically quarantined CI runner subnet at T+60s.');
          addOutput('[Outcome]     : Contained in 0.0s with zero compromised databases. Maintained 98.2% availability.');
          addOutput('[Invariants]  : All mandatory security invariants (Ω) preserved.');
        }
        break;

      case 'scenarios':
        addOutput('=== PRE-PACKAGED MITRE ATT&CK SCENARIOS ===');
        addOutput('1. "black_sky" (Default Benchmark Campaign):');
        addOutput('   - T+15s: Edge SYN Flood (T1499)');
        addOutput('   - T+30s: Auth Credential Stuffing & Hash Starvation (T1110)');
        addOutput('   - T+45s: CI/CD Runner Pool Exhaustion (T1059)');
        addOutput('   - T+60s: Rogue CI Runner Lateral Port Scan to Database (T1046)');
        addOutput('   - T+90s: Recovery Phase & Hysteresis Evaluation');
        addOutput('2. "held_out_evaluation":');
        addOutput('   - T+10s: Public WAF Exploit Probe (T1190)');
        addOutput('   - T+35s: Database Exfiltration Burst (T1048)');
        addOutput('Run via: start black_sky or start held_out_evaluation');
        break;

      case 'clear':
      case 'cls':
        setOutputs([]);
        break;

      default:
        addOutput(`[✖] Command not recognized: "${cmd}". Type "help" to list available commands.`, 'error');
        break;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleCommand(inputVal);
      setInputVal('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length > 0) {
        const nextIdx = historyIndex + 1 < history.length ? historyIndex + 1 : historyIndex;
        setHistoryIndex(nextIdx);
        setInputVal(history[history.length - 1 - nextIdx] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const nextIdx = historyIndex - 1;
        setHistoryIndex(nextIdx);
        setInputVal(history[history.length - 1 - nextIdx] || '');
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInputVal('');
      }
    }
  };

  return (
    <div className={`transition-all duration-300 border-t border-slate-700 bg-[#0b1120] text-slate-200 font-mono text-xs z-30 ${
      isOpen ? (isExpanded ? 'h-96' : 'h-64') : 'h-10'
    } flex flex-col shadow-2xl`}>
      
      {/* Terminal Title Bar */}
      <div 
        onClick={() => !isExpanded && setIsOpen(!isOpen)}
        className="px-4 py-2 bg-[#080d19] border-b border-slate-800 flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center gap-2.5">
          <TerminalIcon className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-slate-200 tracking-wide">
            BASTION X Terminal &amp; Cyber-Range CLI
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            {isRunning ? 'SIMULATION RUNNING' : 'ONLINE'}
          </span>
          <span className="hidden sm:inline text-[10px] text-slate-500">
            (Type "help", "start", "instances", "inspect b", "protocols")
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Quick Action Chips */}
          <div className="hidden md:flex items-center gap-1.5 mr-3">
            <button
              onClick={(e) => { e.stopPropagation(); handleCommand(isRunning ? 'stop' : 'start'); }}
              className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 transition-colors ${
                isRunning ? 'bg-rose-700 hover:bg-rose-600 text-white' : 'bg-cyan-600 hover:bg-cyan-500 text-white'
              }`}
            >
              {isRunning ? <Square className="w-2.5 h-2.5 fill-white" /> : <Play className="w-2.5 h-2.5 fill-white" />}
              {isRunning ? 'stop' : 'start'}
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleCommand('instances'); }}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px]"
            >
              instances
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleCommand('inspect b'); }}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-[10px]"
            >
              inspect b
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleCommand('protocols b'); }}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-emerald-400 text-[10px]"
            >
              protocols b
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleCommand('gemma'); }}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-amber-400 text-[10px]"
            >
              gemma
            </button>
          </div>

          <button
            onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
            className="p-1 hover:text-white text-slate-400"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
            className="p-1 hover:text-white text-slate-400"
            title={isOpen ? "Minimize" : "Open"}
          >
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Terminal Body */}
      {isOpen && (
        <div 
          onClick={() => inputRef.current?.focus()}
          className="flex-1 p-4 overflow-y-auto space-y-1.5 font-mono cursor-text select-text"
        >
          {outputs.map((line) => (
            <div 
              key={line.id} 
              className={`leading-relaxed whitespace-pre-wrap ${
                line.type === 'command' ? 'text-cyan-300 font-bold' :
                (line.type === 'error' ? 'text-rose-400 font-semibold' :
                (line.type === 'success' ? 'text-emerald-400 font-semibold' :
                (line.type === 'system' ? 'text-amber-400' : 'text-slate-300')))
              }`}
            >
              {line.text}
            </div>
          ))}
          <div ref={terminalEndRef} />
        </div>
      )}

      {/* Terminal Input Line */}
      {isOpen && (
        <div className="px-4 py-2.5 bg-[#080d19] border-t border-slate-800 flex items-center gap-2">
          <span className="text-cyan-400 font-bold select-none">bastion-x:~$</span>
          <input
            ref={inputRef}
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Type command ("help", "start", "instances", "inspect b", "protocols b", "gemma")...'
            className="flex-1 bg-transparent border-none outline-none text-slate-100 placeholder-slate-600 font-mono text-xs"
            autoFocus
          />
          <span className="text-[10px] text-slate-500 hidden sm:inline select-none">
            [Enter to run · ↑↓ for history]
          </span>
        </div>
      )}
    </div>
  );
};

