import { ExperimentReport, TrainingStatus, LiveTelemetryMessage } from '../types';

export const API_BASE = '/api/v1';

export async function fetchTrainingStatus(experimentId: string = 'exp-live'): Promise<TrainingStatus> {
  const res = await fetch(`${API_BASE}/training/${experimentId}/status`);
  if (!res.ok) throw new Error('Failed to fetch training status');
  return res.json();
}

export async function startSimulation(params: {
  experiment_id?: string;
  scenario_name?: string;
  max_episodes?: number;
  steps_per_episode?: number;
  use_docker?: boolean;
}) {
  const res = await fetch(`${API_BASE}/training/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      experiment_id: params.experiment_id || 'exp-live',
      scenario_name: params.scenario_name || 'black_sky',
      max_episodes: params.max_episodes || 3,
      steps_per_episode: params.steps_per_episode || 100,
      use_docker: params.use_docker || false,
    }),
  });
  if (!res.ok) throw new Error('Failed to start simulation');
  return res.json();
}

export async function stopSimulation(experimentId: string = 'exp-live') {
  const res = await fetch(`${API_BASE}/training/${experimentId}/stop`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to stop simulation');
  return res.json();
}

export async function fetchExperimentReport(experimentId: string = 'exp-live'): Promise<ExperimentReport> {
  const res = await fetch(`${API_BASE}/experiments/${experimentId}/report`);
  if (!res.ok) throw new Error('Failed to fetch experiment report');
  return res.json();
}

export async function fetchEnvironments() {
  const res = await fetch(`${API_BASE}/environments`);
  if (!res.ok) throw new Error('Failed to fetch environments');
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export function subscribeToTelemetry(
  experimentId: string,
  onMessage: (data: LiveTelemetryMessage) => void,
  onError?: (err: Event) => void
): () => void {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/v1/experiments/${experimentId}`;
  
  let ws: WebSocket | null = null;
  let isClosed = false;

  function connect() {
    if (isClosed) return;
    ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error('Failed to parse WS telemetry:', e);
      }
    };

    ws.onerror = (e) => {
      if (onError) onError(e);
    };

    ws.onclose = () => {
      if (!isClosed) {
        // Auto-reconnect after 2s
        setTimeout(connect, 2000);
      }
    };
  }

  connect();

  return () => {
    isClosed = true;
    if (ws) ws.close();
  };
}

// ============================================================================
// AEGIS ADAPTIVE DEFENSE PLATFORM API EXTENSIONS
// ============================================================================

export async function fetchAegisHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS health');
  return res.json();
}

export async function fetchAegisDefenseState() {
  const res = await fetch(`${API_BASE}/defense/state`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS defense state');
  return res.json();
}

export async function fetchAegisDefenseModules() {
  const res = await fetch(`${API_BASE}/defense/modules`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS defense modules');
  return res.json();
}

export async function fetchAegisIncidents() {
  const res = await fetch(`${API_BASE}/incidents`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS incidents');
  return res.json();
}

export async function fetchAegisEvents() {
  const res = await fetch(`${API_BASE}/events`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS events');
  return res.json();
}

export async function fetchAegisMetricsCompare() {
  const res = await fetch(`${API_BASE}/metrics/compare`);
  if (!res.ok) throw new Error('Failed to fetch AEGIS metrics comparison');
  return res.json();
}

export async function ingestAegisEvent(event: Record<string, any>) {
  const res = await fetch(`${API_BASE}/events/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
  if (!res.ok) throw new Error('Failed to ingest event');
  return res.json();
}

export async function analyzeAegisIncident(incidentId: string) {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}/analyze`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to analyze incident with Gemma');
  return res.json();
}

export async function applyAegisMitigation(payload: {
  incident_id?: string;
  module_id?: string;
  action_id?: string;
  action?: string;
  parameters?: Record<string, any>;
}) {
  const res = await fetch(`${API_BASE}/defense/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to apply defense mitigation');
  return res.json();
}

export async function resetAegisDefenseState() {
  const res = await fetch(`${API_BASE}/defense/state/reset`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reset defense state');
  return res.json();
}
