import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { MetricsCards } from './components/MetricsCards';
import { InstanceCards } from './components/InstanceCards';
import { InstanceDetailModal } from './components/InstanceDetailModal';
import { AvailabilitySection } from './components/AvailabilitySection';
import { BenchmarkTable } from './components/BenchmarkTable';
import { ThreeDomains } from './components/ThreeDomains';
import { DefenceProcessComparison } from './components/DefenceProcessComparison';
import { BenchmarkVisualizations } from './components/BenchmarkVisualizations';
import { ScenarioAttacks } from './components/ScenarioAttacks';
import { SimulationsView } from './components/SimulationsView';
import { PolicyStackView } from './components/PolicyStackView';
import { CyberRangeView } from './components/CyberRangeView';
import { AiReasoningView } from './components/AiReasoningView';
import { TerminalCLI } from './components/TerminalCLI';

import { 
  fetchExperimentReport, 
  fetchTrainingStatus, 
  startSimulation, 
  stopSimulation, 
  subscribeToTelemetry 
} from './services/api';
import { ExperimentReport, EnforcedPolicy } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [selectedScenario, setSelectedScenario] = useState<string>('black_sky');
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('all');
  const [selectedModalInstance, setSelectedModalInstance] = useState<string | null>(null);
  
  // Real-time telemetry state
  const [currentStep, setCurrentStep] = useState<number>(100);
  const [currentEpisode, setCurrentEpisode] = useState<number>(1);
  const [simTime, setSimTime] = useState<number>(100.0);

  // Availability & Metrics
  const [baselineAvail, setBaselineAvail] = useState<number>(39.8);
  const [adaptiveAvail, setAdaptiveAvail] = useState<number>(98.2);
  const [hardenedAvail, setHardenedAvail] = useState<number>(96.5);
  const [experimentalAvail, setExperimentalAvail] = useState<number>(74.8);

  const [baselineBlast, setBaselineBlast] = useState<number>(0.12);
  const [adaptiveBlast, setAdaptiveBlast] = useState<number>(0.00);
  const [hardenedBlast, setHardenedBlast] = useState<number>(0.00);
  const [experimentalBlast, setExperimentalBlast] = useState<number>(0.00);

  const [adaptiveContainment, setAdaptiveContainment] = useState<string | number>('0.0s');
  const [rdiAdaptive, setRdiAdaptive] = useState<number>(1.8);
  const [rdiBaseline, setRdiBaseline] = useState<number>(48.2);

  // Policy & AI
  const [enforcedPolicy, setEnforcedPolicy] = useState<EnforcedPolicy | undefined>();
  const [report, setReport] = useState<ExperimentReport | null>(null);

  // Load initial report from backend
  useEffect(() => {
    fetchExperimentReport('exp-live')
      .then((data) => {
        setReport(data);
        if (data.benchmark_summary) {
          const bs = data.benchmark_summary;
          if (bs.env_a_baseline) setBaselineAvail(parseFloat(bs.env_a_baseline.availability) || 39.8);
          if (bs.env_b_adaptive) setAdaptiveAvail(parseFloat(bs.env_b_adaptive.availability) || 98.2);
          if (bs.env_c_hardened) setHardenedAvail(parseFloat(bs.env_c_hardened.availability) || 96.5);
          if (bs.env_d_experimental) setExperimentalAvail(parseFloat(bs.env_d_experimental.availability) || 74.8);
        }
      })
      .catch((err) => {
        console.warn('Backend report offline or using fallback values:', err);
      });

    // Initial training status check
    fetchTrainingStatus('exp-live')
      .then((st) => {
        setIsRunning(st.is_running);
      })
      .catch(() => {});
  }, []);

  // Connect to live WebSocket telemetry stream
  useEffect(() => {
    const unsubscribe = subscribeToTelemetry('exp-live', (data) => {
      if (data.event_type === 'environment.telemetry' && data.workers) {
        setIsRunning(true);
        setCurrentStep(data.step);
        setCurrentEpisode(data.episode);
        setSimTime(data.step * 1.0);

        const w = data.workers;
        if (w.env_a_baseline?.metrics) {
          setBaselineAvail(w.env_a_baseline.metrics.effective_availability_pct);
          setBaselineBlast(w.env_a_baseline.metrics.blast_radius_factor);
          setRdiBaseline(w.env_a_baseline.metrics.resilience_degradation_index);
        }
        if (w.env_b_adaptive?.metrics) {
          setAdaptiveAvail(w.env_b_adaptive.metrics.effective_availability_pct);
          setAdaptiveBlast(w.env_b_adaptive.metrics.blast_radius_factor);
          setRdiAdaptive(w.env_b_adaptive.metrics.resilience_degradation_index);
          const mttc = w.env_b_adaptive.metrics.mean_time_to_containment_s;
          setAdaptiveContainment(mttc !== null && mttc !== undefined ? `${mttc.toFixed(1)}s` : '0.0s');
        }
        if (w.env_c_hardened?.metrics) {
          setHardenedAvail(w.env_c_hardened.metrics.effective_availability_pct);
          setHardenedBlast(w.env_c_hardened.metrics.blast_radius_factor);
        }
        if (w.env_d_experimental?.metrics) {
          setExperimentalAvail(w.env_d_experimental.metrics.effective_availability_pct);
          setExperimentalBlast(w.env_d_experimental.metrics.blast_radius_factor);
        }
        if (w.env_b_adaptive?.enforced_policy) {
          setEnforcedPolicy(w.env_b_adaptive.enforced_policy);
        }
      } else if (data.event_type === 'experiment.completed') {
        setIsRunning(false);
        // Refresh comprehensive report
        fetchExperimentReport('exp-live').then(setReport).catch(() => {});
      }
    });

    return () => unsubscribe();
  }, []);

  const handleRunSimulation = async (scenario?: string) => {
    const sc = scenario || selectedScenario;
    try {
      setIsRunning(true);
      await startSimulation({
        experiment_id: 'exp-live',
        scenario_name: sc,
        max_episodes: 2,
        steps_per_episode: 50,
        use_docker: false
      });
    } catch (e) {
      console.error('Failed to trigger simulation:', e);
      setIsRunning(false);
      throw e;
    }
  };

  const handleStopSimulation = async () => {
    try {
      await stopSimulation('exp-live');
      setIsRunning(false);
    } catch (e) {
      console.error('Failed to stop simulation:', e);
      throw e;
    }
  };

  const handleSelectInstance = (instanceId: string) => {
    setSelectedModalInstance(instanceId);
    setSelectedEnvironment(instanceId);
  };

  // Get metrics for current modal selection
  const getModalAvailability = () => {
    if (selectedModalInstance === 'env_a_baseline') return baselineAvail;
    if (selectedModalInstance === 'env_b_adaptive') return adaptiveAvail;
    if (selectedModalInstance === 'env_c_hardened') return hardenedAvail;
    return experimentalAvail;
  };

  const getModalBlastRadius = () => {
    if (selectedModalInstance === 'env_a_baseline') return baselineBlast;
    if (selectedModalInstance === 'env_b_adaptive') return adaptiveBlast;
    if (selectedModalInstance === 'env_c_hardened') return hardenedBlast;
    return experimentalBlast;
  };

  const getModalContainment = () => {
    if (selectedModalInstance === 'env_a_baseline') return 'UNCONTAINED';
    if (selectedModalInstance === 'env_b_adaptive') return adaptiveContainment;
    if (selectedModalInstance === 'env_c_hardened') return '0.0s';
    return '6.0s';
  };

  const getModalRdi = () => {
    if (selectedModalInstance === 'env_a_baseline') return rdiBaseline;
    if (selectedModalInstance === 'env_b_adaptive') return rdiAdaptive;
    if (selectedModalInstance === 'env_c_hardened') return 3.5;
    return 25.2;
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex">
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Header */}
        <Header 
          isRunning={isRunning}
          onRunSimulation={() => handleRunSimulation()}
          onStopSimulation={handleStopSimulation}
          selectedScenario={selectedScenario}
          onSelectScenario={setSelectedScenario}
          selectedEnvironment={selectedEnvironment}
          onSelectEnvironment={(env) => {
            setSelectedEnvironment(env);
            if (env !== 'all') setSelectedModalInstance(env);
          }}
          step={currentStep}
          episode={currentEpisode}
        />

        {/* Scrollable Dashboard Viewport */}
        <div className="flex-1 overflow-y-auto">
          <main className="p-8 space-y-8 max-w-7xl pb-24">
            {currentTab === 'overview' && (
              <>
                {/* 1. Top KPI Summary Cards */}
                <MetricsCards 
                  adaptiveAvailability={adaptiveAvail}
                  baselineAvailability={baselineAvail}
                  containmentTime={adaptiveContainment}
                  adaptiveBlastRadius={adaptiveBlast}
                  baselineBlastRadius={baselineBlast}
                />

                {/* 2. Interactive 4 Parallel Instance Cards (Click to inspect protocol simulation) */}
                <InstanceCards 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                  baselineBlast={baselineBlast}
                  adaptiveBlast={adaptiveBlast}
                  hardenedBlast={hardenedBlast}
                  experimentalBlast={experimentalBlast}
                  adaptiveContainment={adaptiveContainment}
                  onSelectInstance={handleSelectInstance}
                  selectedInstanceId={selectedModalInstance}
                />

                {/* 3. Availability Comparison Bar Chart & DDPS Guard */}
                <AvailabilitySection 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                />

                {/* 4. Black Sky Benchmark Table */}
                <BenchmarkTable 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                  baselineBlast={baselineBlast}
                  adaptiveBlast={adaptiveBlast}
                  hardenedBlast={hardenedBlast}
                  experimentalBlast={experimentalBlast}
                  mttcAdaptive={adaptiveContainment}
                  rdiAdaptive={rdiAdaptive}
                  rdiBaseline={rdiBaseline}
                  onSelectInstance={handleSelectInstance}
                />

                {/* 5. One Policy Stack, Three Isolated Domains */}
                <ThreeDomains />

                {/* 6. Defence Process Comparison */}
                <DefenceProcessComparison 
                  baselineAvail={baselineAvail}
                  baselineBlast={baselineBlast}
                  adaptiveAvail={adaptiveAvail}
                  adaptiveBlast={adaptiveBlast}
                  adaptiveContainment={adaptiveContainment}
                />

                {/* 7. Benchmark Visualizations */}
                <BenchmarkVisualizations 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                  baselineBlast={baselineBlast}
                  adaptiveBlast={adaptiveBlast}
                  hardenedBlast={hardenedBlast}
                  experimentalBlast={experimentalBlast}
                  adaptiveContainment={adaptiveContainment}
                  rdiBaseline={rdiBaseline}
                  rdiAdaptive={rdiAdaptive}
                />

                {/* 8. Scenario Attacks */}
                <ScenarioAttacks />
              </>
            )}

            {currentTab === 'simulations' && (
              <SimulationsView 
                currentStep={currentStep}
                simTime={simTime}
              />
            )}

            {currentTab === 'policy-stack' && (
              <PolicyStackView 
                enforcedPolicy={enforcedPolicy}
              />
            )}

            {currentTab === 'cyber-range' && (
              <CyberRangeView />
            )}

            {currentTab === 'benchmarks' && (
              <div className="space-y-6">
                <BenchmarkTable 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                  baselineBlast={baselineBlast}
                  adaptiveBlast={adaptiveBlast}
                  hardenedBlast={hardenedBlast}
                  experimentalBlast={experimentalBlast}
                  mttcAdaptive={adaptiveContainment}
                  rdiAdaptive={rdiAdaptive}
                  rdiBaseline={rdiBaseline}
                  onSelectInstance={handleSelectInstance}
                />
                <BenchmarkVisualizations 
                  baselineAvail={baselineAvail}
                  adaptiveAvail={adaptiveAvail}
                  hardenedAvail={hardenedAvail}
                  experimentalAvail={experimentalAvail}
                  baselineBlast={baselineBlast}
                  adaptiveBlast={adaptiveBlast}
                  hardenedBlast={hardenedBlast}
                  experimentalBlast={experimentalBlast}
                  adaptiveContainment={adaptiveContainment}
                  rdiBaseline={rdiBaseline}
                  rdiAdaptive={rdiAdaptive}
                />
              </div>
            )}

            {currentTab === 'ai-reasoning' && (
              <AiReasoningView 
                explanation={report?.gemma_ai_explanation}
              />
            )}

            {currentTab === 'terminal' && (
              <div className="space-y-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 tracking-tight">Dedicated Cyber-Range Terminal Console</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Direct CLI control for instance navigation, dynamic protocol triggers, and simulation lifecycle</p>
                </div>
                <div className="p-4 bg-white border border-slate-200 rounded-lg text-xs text-slate-600">
                  <p className="font-semibold text-slate-800 mb-2">Available Command Quick Reference:</p>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono">
                    <li><span className="text-[#dc2626] font-bold">start [scenario]</span> : Launch parallel simulation</li>
                    <li><span className="text-[#dc2626] font-bold">stop</span> : Terminate active run</li>
                    <li><span className="text-[#dc2626] font-bold">instances</span> : Print live metrics for all 4 instances</li>
                    <li><span className="text-[#dc2626] font-bold">inspect &lt;a|b|c|d&gt;</span> : Open protocol inspector modal</li>
                    <li><span className="text-[#dc2626] font-bold">protocols &lt;a|b&gt;</span> : Display OSI dynamic modulation</li>
                    <li><span className="text-[#dc2626] font-bold">topology</span> : Print 8-node canonical status</li>
                    <li><span className="text-[#dc2626] font-bold">gemma</span> : Fetch Gemma 4 AI root-cause report</li>
                    <li><span className="text-[#dc2626] font-bold">clear</span> : Clear console buffer</li>
                  </ul>
                </div>
              </div>
            )}
          </main>
        </div>

        {/* Docked Interactive Terminal CLI (Sticky bottom console) */}
        <TerminalCLI
          isRunning={isRunning}
          onStartSimulation={handleRunSimulation}
          onStopSimulation={handleStopSimulation}
          onInspectInstance={handleSelectInstance}
          baselineAvail={baselineAvail}
          adaptiveAvail={adaptiveAvail}
          hardenedAvail={hardenedAvail}
          experimentalAvail={experimentalAvail}
          baselineBlast={baselineBlast}
          adaptiveBlast={adaptiveBlast}
          hardenedBlast={hardenedBlast}
          experimentalBlast={experimentalBlast}
          adaptiveContainment={adaptiveContainment}
          rdiBaseline={rdiBaseline}
          rdiAdaptive={rdiAdaptive}
          currentStep={currentStep}
          currentEpisode={currentEpisode}
          simTime={simTime}
          report={report}
          enforcedPolicy={enforcedPolicy}
        />
      </div>

      {/* Instance Simulation Detail & Protocol Inspector Modal */}
      {selectedModalInstance && (
        <InstanceDetailModal
          instanceId={selectedModalInstance}
          onClose={() => {
            setSelectedModalInstance(null);
            setSelectedEnvironment('all');
          }}
          availability={getModalAvailability()}
          blastRadius={getModalBlastRadius()}
          containment={getModalContainment()}
          rdi={getModalRdi()}
          simTime={simTime}
          step={currentStep}
          enforcedPolicy={enforcedPolicy}
        />
      )}
    </div>
  );
};

export default App;
