import { useState, useEffect, useCallback, useRef } from 'react';

export type BackendMode = 'live' | 'mock';

export interface BackendStatus {
  mode: BackendMode;
  available: boolean;
  checking: boolean;
  nodeStatus: string; // 'healthy' | 'degraded' | 'unreachable' | 'unknown'
  lastChecked: number;
}

declare global {
  interface Window {
    ariaElectron?: {
      getSystemInfo: () => Promise<any>;
      getAppVersion: () => Promise<string>;
      getNodeStatus: () => Promise<any>;
      startNode: () => Promise<string>;
      stopNode: () => Promise<string>;
      getModels: () => Promise<any>;
      downloadModel: (name: string) => Promise<any>;
      sendInference: (prompt: string, model: string, language?: string) => Promise<any>;
      checkBackendStatus: () => Promise<{
        available: boolean;
        status?: string;
        node?: any;
        reason?: string;
      }>;
      onNodeStatus: (callback: (status: any) => void) => () => void;
      platform: string;
    };
  }
}

const CHECK_INTERVAL = 10000; // Check every 10 seconds

export function useBackend() {
  const [status, setStatus] = useState<BackendStatus>({
    mode: 'mock',
    available: false,
    checking: true,
    nodeStatus: 'unknown',
    lastChecked: 0,
  });
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const checkBackend = useCallback(async () => {
    if (!window.ariaElectron?.checkBackendStatus) {
      setStatus((prev) => ({
        ...prev,
        mode: 'mock',
        available: false,
        checking: false,
        nodeStatus: 'no-electron',
      }));
      return;
    }

    setStatus((prev) => ({ ...prev, checking: true }));

    try {
      const result = await window.ariaElectron.checkBackendStatus();
      setStatus({
        mode: result.available ? 'live' : 'mock',
        available: result.available,
        checking: false,
        nodeStatus: result.available ? (result.status || 'healthy') : (result.reason || 'unreachable'),
        lastChecked: Date.now(),
      });
    } catch {
      setStatus({
        mode: 'mock',
        available: false,
        checking: false,
        nodeStatus: 'error',
        lastChecked: Date.now(),
      });
    }
  }, []);

  useEffect(() => {
    // Check immediately on mount
    checkBackend();

    // Then check periodically
    intervalRef.current = setInterval(checkBackend, CHECK_INTERVAL);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [checkBackend]);

  return { ...status, refresh: checkBackend };
}
