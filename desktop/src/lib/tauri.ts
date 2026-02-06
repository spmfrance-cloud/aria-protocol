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
  return {
    os: navigator.platform,
    arch: 'unknown',
    version: '0.5.2',
  };
}

export async function getAppVersion(): Promise<string> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_app_version') as Promise<string>;
  }
  return '0.5.2';
}

export async function getNodeStatus(): Promise<NodeStatus> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_node_status') as Promise<NodeStatus>;
  }
  return {
    running: false,
    peer_count: 0,
    uptime_seconds: 0,
    version: '0.5.2',
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
  return 'Mock: Node stopped (dev mode)';
}

export async function getModels(): Promise<ModelInfo[]> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('get_models') as Promise<ModelInfo[]>;
  }
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
  return { model: name, progress: 0, status: 'mock' };
}

export async function sendInference(prompt: string, model: string): Promise<InferenceResponse> {
  const invoke = await getTauriInvoke();
  if (invoke) {
    return invoke('send_inference', { prompt, model }) as Promise<InferenceResponse>;
  }
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
