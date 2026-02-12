/**
 * Tauri command wrapper for ARIA Desktop.
 *
 * Provides typed functions for all Tauri invoke commands.
 * Falls back gracefully when running outside of Tauri (browser dev mode).
 */

// ── Types ──────────────────────────────────────────────────────────

export interface NodeStatus {
  running: boolean;
  peer_count: number;
  uptime_seconds: number;
  version: string;
  backend: string;
  model: string | null;
  llama_cli_available?: boolean;
}

export interface ModelInfo {
  name: string;
  params: string;
  size: string;
  downloaded: boolean;
  description: string;
}

export interface InferenceResponse {
  text: string;
  tokens_per_second: number;
  model: string;
  energy_mj: number;
  backend?: string;
}

export interface DownloadProgress {
  model: string;
  progress: number;
  status: string;
}

export interface SystemInfo {
  os: string;
  arch: string;
  version: string;
}

export interface BackendInfo {
  python_found: boolean;
  python_path: string;
  python_version: string;
  aria_installed: boolean;
  aria_version: string;
  llama_cli_found: boolean;
  models_found: number;
}

export interface StartNodeResult {
  status: string;
  backend: string;
  port: number;
  pid: number;
  models_available: number;
}

export interface EnergySavings {
  energy_saved_kwh: number;
  reduction_percent: number;
  co2_saved_kg: number;
  cost_saved_usd: number;
}

export interface EnergyStats {
  total_inferences: number;
  total_tokens_generated: number;
  total_energy_kwh: number;
  avg_energy_per_token_mj: number;
  session_uptime_seconds: number;
  savings: EnergySavings;
}

// ── Tauri Detection ────────────────────────────────────────────────

/**
 * Check if the app is running inside Tauri.
 */
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/**
 * Dynamically import Tauri invoke. Returns null if not in Tauri context.
 */
async function getTauriInvoke(): Promise<((cmd: string, args?: Record<string, unknown>) => Promise<unknown>) | null> {
  if (!isTauri()) return null;
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    return invoke;
  } catch {
    return null;
  }
}

// ── Commands ───────────────────────────────────────────────────────

export async function getSystemInfo(): Promise<SystemInfo> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_system_info') as Promise<SystemInfo>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return {
    os: navigator.platform,
    arch: 'unknown',
    version: '0.5.5',
  };
}

export async function getAppVersion(): Promise<string> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_app_version') as Promise<string>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return '0.5.5';
}

export async function getNodeStatus(): Promise<NodeStatus> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_node_status') as Promise<NodeStatus>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return {
    running: false,
    peer_count: 0,
    uptime_seconds: 0,
    version: '0.5.5',
    backend: 'mock',
    model: null,
    llama_cli_available: false,
  };
}

export async function startNode(): Promise<StartNodeResult> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('start_node') as Promise<StartNodeResult>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return {
    status: 'mock',
    backend: 'mock',
    port: 3000,
    pid: 0,
    models_available: 0,
  };
}

export async function stopNode(): Promise<string> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('stop_node') as Promise<string>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return 'Mock: Node stopped (dev mode)';
}

export async function getModels(): Promise<ModelInfo[]> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    try {
      return await invoke('get_models') as Promise<ModelInfo[]>;
    } catch (e) {
      console.warn('[tauri] get_models failed, trying HTTP fallback:', e);
    }
  }

  // HTTP fallback — try the Python API server directly
  try {
    const response = await fetch('http://127.0.0.1:3000/v1/models');
    if (response.ok) {
      const data = await response.json();
      if (data?.data) {
        return data.data.map((m: Record<string, unknown>) => {
          const meta = m.meta as Record<string, unknown> | undefined;
          return {
            name: (meta?.display_name as string) || (m.id as string),
            params: (meta?.params as string) || '?',
            size: `${(meta?.params as string) || '?'} params`,
            downloaded: (m.ready as boolean) || false,
            description: `${m.id} — 1-bit quantization`,
          };
        });
      }
    }
  } catch (e) {
    console.warn('[tauri] HTTP fallback for models also failed:', e);
  }

  // Last resort — static defaults
  return [
    { name: 'BitNet-b1.58-large', params: '0.7B', size: '400 MB', downloaded: false, description: 'Fast, lightweight model for quick responses' },
    { name: 'BitNet-b1.58-2B-4T', params: '2.4B', size: '1.3 GB', downloaded: false, description: 'Best balance of speed and quality' },
    { name: 'Llama3-8B-1.58', params: '8.0B', size: '4.2 GB', downloaded: false, description: 'Most capable model, requires more RAM' },
  ];
}

export async function downloadModel(name: string): Promise<DownloadProgress> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('download_model', { name }) as Promise<DownloadProgress>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return { model: name, progress: 0, status: 'mock' };
}

export async function sendInference(prompt: string, model: string): Promise<InferenceResponse> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('send_inference', { prompt, model }) as Promise<InferenceResponse>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return {
    text: `[Dev mode] Mock response for: "${prompt}"`,
    tokens_per_second: 0,
    model,
    energy_mj: 0,
    backend: 'mock',
  };
}

export async function getBackendInfo(): Promise<BackendInfo> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_backend_info') as Promise<BackendInfo>;
  }
  // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
  return {
    python_found: false,
    python_path: '',
    python_version: '',
    aria_installed: false,
    aria_version: '',
    llama_cli_found: false,
    models_found: 0,
  };
}

const DEFAULT_ENERGY: EnergyStats = {
  total_inferences: 0,
  total_tokens_generated: 0,
  total_energy_kwh: 0,
  avg_energy_per_token_mj: 0,
  session_uptime_seconds: 0,
  savings: {
    energy_saved_kwh: 0,
    reduction_percent: 0,
    co2_saved_kg: 0,
    cost_saved_usd: 0,
  },
};

export async function getEnergyStats(): Promise<EnergyStats> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    try {
      return await invoke('get_energy_stats') as Promise<EnergyStats>;
    } catch (e) {
      console.warn('[tauri] get_energy_stats failed, trying HTTP:', e);
    }
  }

  // HTTP fallback
  try {
    const response = await fetch('http://127.0.0.1:3000/v1/energy');
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    console.warn('[tauri] HTTP energy fallback failed:', e);
  }

  return DEFAULT_ENERGY;
}
