import { useState, useEffect, useCallback, useRef } from 'react';
import { getNodeStatus, isTauri } from '@/lib/tauri';

export type BackendMode = 'live' | 'mock' | 'offline';

export interface BackendStatus {
  mode: BackendMode;
  available: boolean;
  checking: boolean;
  nodeRunning: boolean;
  backend: string;           // 'native' | 'simulation' | 'mock' | 'none'
  modelsCount: number;
  uptime: number;
  llamaCliAvailable: boolean;
  pythonVersion: string;
  lastChecked: number;
}

const CHECK_INTERVAL = 10000; // Check every 10 seconds

export function useBackend() {
  const [status, setStatus] = useState<BackendStatus>({
    mode: 'offline',
    available: false,
    checking: true,
    nodeRunning: false,
    backend: 'none',
    modelsCount: 0,
    uptime: 0,
    llamaCliAvailable: false,
    pythonVersion: '',
    lastChecked: 0,
  });
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const checkBackend = useCallback(async () => {
    setStatus((prev) => ({ ...prev, checking: true }));

    try {
      const nodeStatus = await getNodeStatus();

      if (nodeStatus.running) {
        // Backend is running — determine mode
        setStatus({
          mode: 'live',
          available: true,
          checking: false,
          nodeRunning: true,
          backend: nodeStatus.backend,
          modelsCount: 0,
          uptime: nodeStatus.uptime_seconds,
          llamaCliAvailable: nodeStatus.llama_cli_available ?? false,
          pythonVersion: '',
          lastChecked: Date.now(),
        });
      } else if (!isTauri()) {
        // Not in Tauri — always mock mode
        setStatus({
          mode: 'mock',
          available: false,
          checking: false,
          nodeRunning: false,
          backend: 'mock',
          modelsCount: 0,
          uptime: 0,
          llamaCliAvailable: false,
          pythonVersion: '',
          lastChecked: Date.now(),
        });
      } else {
        // In Tauri but node not running
        setStatus({
          mode: 'offline',
          available: false,
          checking: false,
          nodeRunning: false,
          backend: 'none',
          modelsCount: 0,
          uptime: 0,
          llamaCliAvailable: false,
          pythonVersion: '',
          lastChecked: Date.now(),
        });
      }
    } catch {
      setStatus({
        mode: isTauri() ? 'offline' : 'mock',
        available: false,
        checking: false,
        nodeRunning: false,
        backend: 'none',
        modelsCount: 0,
        uptime: 0,
        llamaCliAvailable: false,
        pythonVersion: '',
        lastChecked: Date.now(),
      });
    }
  }, []);

  useEffect(() => {
    checkBackend();
    intervalRef.current = setInterval(checkBackend, CHECK_INTERVAL);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [checkBackend]);

  return { ...status, refresh: checkBackend };
}
