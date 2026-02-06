import { useState, useCallback, useRef, useEffect } from "react";
import { getModels as fetchModels } from "@/lib/tauri";

export type ModelStatus = "available" | "downloading" | "installed";

export interface ModelInfo {
  id: string;
  name: string;
  params: string;
  size: string;
  performance: string;
  ram: string;
  description: string;
  huggingface: string;
  benchmarks: {
    tokensPerSec: number;
    ttft: string;
    energy: string;
  };
  requirements: {
    ram: string;
    disk: string;
  };
  recommended?: boolean;
}

export interface ModelState {
  status: ModelStatus;
  progress: number;
  speed: string;
  eta: string;
}

// Default model definitions with full metadata
const DEFAULT_MODELS: ModelInfo[] = [
  {
    id: "bitnet-b158-large",
    name: "BitNet-b1.58-large",
    params: "0.7B",
    size: "400 MB",
    performance: "89.65 t/s",
    ram: "400 MB",
    description:
      "Compact 1-bit LLM optimized for edge devices. Delivers exceptional throughput with minimal resource usage, ideal for real-time inference on consumer hardware.",
    huggingface: "https://huggingface.co/microsoft/BitNet-b1.58-large",
    benchmarks: {
      tokensPerSec: 89.65,
      ttft: "45ms",
      energy: "1.2 mJ/token",
    },
    requirements: {
      ram: "400 MB",
      disk: "250 MB",
    },
  },
  {
    id: "bitnet-b158-2b-4t",
    name: "BitNet-b1.58-2B-4T",
    params: "2.4B",
    size: "1.3 GB",
    performance: "36.94 t/s",
    ram: "1.3 GB",
    description:
      "The recommended general-purpose BitNet model. Trained on 4 trillion tokens, it offers the best balance between performance and resource efficiency for most use cases.",
    huggingface: "https://huggingface.co/microsoft/BitNet-b1.58-2B-4T",
    benchmarks: {
      tokensPerSec: 36.94,
      ttft: "120ms",
      energy: "2.4 mJ/token",
    },
    requirements: {
      ram: "1.3 GB",
      disk: "800 MB",
    },
    recommended: true,
  },
  {
    id: "llama3-8b-158",
    name: "Llama3-8B-1.58",
    params: "8B",
    size: "4.2 GB",
    performance: "15.03 t/s",
    ram: "4.2 GB",
    description:
      "1-bit quantized Llama 3 8B model. Provides strong language understanding and generation capabilities with significantly reduced memory footprint compared to the original.",
    huggingface: "https://huggingface.co/HF1BitLLM/Llama3-8B-1.58-100B-tokens",
    benchmarks: {
      tokensPerSec: 15.03,
      ttft: "280ms",
      energy: "5.8 mJ/token",
    },
    requirements: {
      ram: "4.2 GB",
      disk: "2.5 GB",
    },
  },
];

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>(DEFAULT_MODELS);
  const [modelStates, setModelStates] = useState<Record<string, ModelState>>({});
  const intervalsRef = useRef<Record<string, ReturnType<typeof setInterval>>>({});

  // On mount, fetch real models from backend and mark downloaded ones
  useEffect(() => {
    let cancelled = false;

    async function loadModels() {
      try {
        const backendModels = await fetchModels();

        if (cancelled) return;

        // Map backend models to update the "downloaded" status
        // The backend returns: { name, params, size, downloaded, description }
        const updatedStates: Record<string, ModelState> = {};

        for (const bm of backendModels) {
          // Find matching default model
          const matchId = DEFAULT_MODELS.find(
            (m) =>
              m.name.toLowerCase() === bm.name.toLowerCase() ||
              m.id.toLowerCase().replace(/-/g, "") ===
                bm.name.toLowerCase().replace(/-/g, "").replace(/\./g, "")
          )?.id;

          if (matchId && bm.downloaded) {
            updatedStates[matchId] = {
              status: "installed",
              progress: 100,
              speed: "",
              eta: "",
            };
          }
        }

        // Also update model sizes from backend if available
        setModels((prev) =>
          prev.map((m) => {
            const bm = backendModels.find(
              (b) =>
                b.name.toLowerCase() === m.name.toLowerCase() ||
                m.id.toLowerCase().replace(/-/g, "") ===
                  b.name.toLowerCase().replace(/-/g, "").replace(/\./g, "")
            );
            if (bm) {
              return {
                ...m,
                size: bm.size || m.size,
                downloaded: bm.downloaded,
              } as ModelInfo;
            }
            return m;
          })
        );

        setModelStates((prev) => ({ ...prev, ...updatedStates }));
      } catch {
        // Fall back to defaults on error
      }
    }

    loadModels();

    return () => {
      cancelled = true;
    };
  }, []);

  const getModelState = useCallback(
    (modelId: string): ModelState => {
      return (
        modelStates[modelId] ?? {
          status: "available",
          progress: 0,
          speed: "",
          eta: "",
        }
      );
    },
    [modelStates]
  );

  const getInstalledModels = useCallback(() => {
    return models.filter(
      (m) => modelStates[m.id]?.status === "installed"
    );
  }, [models, modelStates]);

  const downloadModel = useCallback((modelId: string) => {
    // Clear any existing interval for this model
    if (intervalsRef.current[modelId]) {
      clearInterval(intervalsRef.current[modelId]);
    }

    setModelStates((prev) => ({
      ...prev,
      [modelId]: {
        status: "downloading",
        progress: 0,
        speed: "0 MB/s",
        eta: "Estimating...",
      },
    }));

    const startTime = Date.now();
    const totalDuration = 5000; // 5 seconds

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min((elapsed / totalDuration) * 100, 100);
      const remaining = Math.max(0, (totalDuration - elapsed) / 1000);

      // Simulate variable download speed
      const baseSpeed = 8 + Math.random() * 12;
      const speed = `${baseSpeed.toFixed(1)} MB/s`;
      const eta =
        remaining > 0 ? `${Math.ceil(remaining)}s remaining` : "Finishing...";

      if (progress >= 100) {
        clearInterval(interval);
        delete intervalsRef.current[modelId];
        setModelStates((prev) => ({
          ...prev,
          [modelId]: {
            status: "installed",
            progress: 100,
            speed: "",
            eta: "",
          },
        }));
      } else {
        setModelStates((prev) => ({
          ...prev,
          [modelId]: {
            status: "downloading",
            progress: Math.round(progress),
            speed,
            eta,
          },
        }));
      }
    }, 50);

    intervalsRef.current[modelId] = interval;
  }, []);

  const cancelDownload = useCallback((modelId: string) => {
    if (intervalsRef.current[modelId]) {
      clearInterval(intervalsRef.current[modelId]);
      delete intervalsRef.current[modelId];
    }

    setModelStates((prev) => ({
      ...prev,
      [modelId]: {
        status: "available",
        progress: 0,
        speed: "",
        eta: "",
      },
    }));
  }, []);

  const removeModel = useCallback((modelId: string) => {
    if (intervalsRef.current[modelId]) {
      clearInterval(intervalsRef.current[modelId]);
      delete intervalsRef.current[modelId];
    }

    setModelStates((prev) => {
      const next = { ...prev };
      delete next[modelId];
      return next;
    });
  }, []);

  return {
    models,
    modelStates,
    getModelState,
    getInstalledModels,
    downloadModel,
    cancelDownload,
    removeModel,
  };
}
