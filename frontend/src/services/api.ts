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

