/**
 * Unified API interface for ARIA Desktop.
 *
 * Automatically routes calls through:
 * 1. Tauri invoke (when running as Tauri app)
 * 2. Electron IPC (when running as Electron app)
 * 3. Mock data (when running in browser dev mode)
 */

import * as tauri from './tauri';
import type {
  NodeStatus,
  ModelInfo,
  InferenceResponse,
  DownloadProgress,
  SystemInfo,
} from './tauri';

// Re-export types
export type { NodeStatus, ModelInfo, InferenceResponse, DownloadProgress, SystemInfo };

// ── Runtime Detection ──────────────────────────────────────────────

interface ElectronAPI {
  getSystemInfo: () => Promise<SystemInfo>;
  getAppVersion: () => Promise<string>;
  getNodeStatus: () => Promise<NodeStatus>;
  startNode: () => Promise<string>;
  stopNode: () => Promise<string>;
  getModels: () => Promise<ModelInfo[]>;
  downloadModel: (name: string) => Promise<DownloadProgress>;
  sendInference: (prompt: string, model: string) => Promise<InferenceResponse>;
  onNodeStatus: (callback: (status: NodeStatus) => void) => () => void;
  platform: string;
}

function getElectronAPI(): ElectronAPI | null {
  if (typeof window !== 'undefined' && 'ariaElectron' in window) {
    return (window as unknown as { ariaElectron: ElectronAPI }).ariaElectron;
  }
  return null;
}

type Runtime = 'tauri' | 'electron' | 'web';

export function detectRuntime(): Runtime {
  if (tauri.isTauri()) return 'tauri';
  if (getElectronAPI()) return 'electron';
  return 'web';
}

// ── Unified API ────────────────────────────────────────────────────

export async function getSystemInfo(): Promise<SystemInfo> {
  const electron = getElectronAPI();
  if (electron) return electron.getSystemInfo();
  return tauri.getSystemInfo();
}

export async function getAppVersion(): Promise<string> {
  const electron = getElectronAPI();
  if (electron) return electron.getAppVersion();
  return tauri.getAppVersion();
}

export async function getNodeStatus(): Promise<NodeStatus> {
  const electron = getElectronAPI();
  if (electron) return electron.getNodeStatus();
  return tauri.getNodeStatus();
}

export async function startNode(): Promise<string> {
  const electron = getElectronAPI();
  if (electron) return electron.startNode();
  return tauri.startNode();
}

export async function stopNode(): Promise<string> {
  const electron = getElectronAPI();
  if (electron) return electron.stopNode();
  return tauri.stopNode();
}

export async function getModels(): Promise<ModelInfo[]> {
  const electron = getElectronAPI();
  if (electron) return electron.getModels();
  return tauri.getModels();
}

export async function downloadModel(name: string): Promise<DownloadProgress> {
  const electron = getElectronAPI();
  if (electron) return electron.downloadModel(name);
  return tauri.downloadModel(name);
}

export async function sendInference(prompt: string, model: string): Promise<InferenceResponse> {
  const electron = getElectronAPI();
  if (electron) return electron.sendInference(prompt, model);
  return tauri.sendInference(prompt, model);
}

/**
 * Subscribe to node status changes (Electron only).
 * Returns an unsubscribe function, or null if not in Electron.
 */
export function onNodeStatusChange(callback: (status: NodeStatus) => void): (() => void) | null {
  const electron = getElectronAPI();
  if (electron) return electron.onNodeStatus(callback);
  return null;
}
