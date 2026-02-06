import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { getEnergyStats } from "@/lib/tauri";
import type { EnergyStats as BackendEnergyStats } from "@/lib/tauri";

export type Period = "today" | "week" | "month" | "all";

export interface DailyData {
  date: string;
  label: string;
  tokens: number;
  energyMj: number;
  energyKwh: number;
  costAria: number;
  costCloud: number;
  costGpu: number;
  co2Avoided: number;
}

export interface EnergyStats {
  totalEnergyKwh: number;
  co2AvoidedKg: number;
  moneySaved: number;
  cloudComparisonPercent: number;
  totalTokens: number;
  avgEnergyPerToken: number;
  avgTokensPerDay: number;
}

export interface Achievement {
  id: string;
  icon: string;
  title: string;
  description: string;
  unlocked: boolean;
  progress: number;
  target: number;
}

export interface ComparisonData {
  name: string;
  energyPerToken: number;
  costPerToken: number;
  color: string;
  label: string;
}

// Static comparison data — real benchmark numbers
const COMPARISON_DATA: ComparisonData[] = [
  {
    name: "ARIA Protocol",
    energyPerToken: 28,
    costPerToken: 0.000002,
    color: "#10b981",
    label: "Local 1-bit inference",
  },
  {
    name: "Cloud API",
    energyPerToken: 7000,
    costPerToken: 0.015,
    color: "#6366f1",
    label: "GPT-4 API pricing",
  },
  {
    name: "RTX 4090",
    energyPerToken: 5625,
    costPerToken: 0.0008,
    color: "#f59e0b",
    label: "Local GPU inference",
  },
];

/**
 * Build chart data points from the rolling inference history.
 */
function buildChartData(
  history: Array<{ timestamp: number; energy_mj: number; tokens: number }>
): DailyData[] {
  if (!history || history.length === 0) return [];

  const CLOUD_MJ_PER_TOKEN = 7000;
  const CO2_FACTOR = 0.5; // kg CO2 per kWh
  const ARIA_COST_PER_TOKEN = 0.000002;
  const CLOUD_COST_PER_TOKEN = 0.000015;
  const GPU_COST_PER_TOKEN = 0.0000008;
  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];

  return history.map((entry) => {
    const date = new Date(entry.timestamp * 1000);
    const energyKwh = entry.energy_mj / 3_600_000;
    const cloudEnergyKwh = (entry.tokens * CLOUD_MJ_PER_TOKEN) / 3_600_000;
    const hh = String(date.getHours()).padStart(2, "0");
    const mm = String(date.getMinutes()).padStart(2, "0");

    return {
      date: date.toISOString().split("T")[0],
      label: `${monthNames[date.getMonth()]} ${date.getDate()} ${hh}:${mm}`,
      tokens: entry.tokens,
      energyMj: Math.round(entry.energy_mj * 100) / 100,
      energyKwh: Math.round(energyKwh * 1_000_000) / 1_000_000,
      costAria: Math.round(entry.tokens * ARIA_COST_PER_TOKEN * 100_000) / 100_000,
      costCloud: Math.round(entry.tokens * CLOUD_COST_PER_TOKEN * 100_000) / 100_000,
      costGpu: Math.round(entry.tokens * GPU_COST_PER_TOKEN * 100_000) / 100_000,
      co2Avoided: Math.round((cloudEnergyKwh - energyKwh) * CO2_FACTOR * 100_000) / 100_000,
    };
  });
}

/**
 * Derive achievement progress from real accumulated stats.
 */
function deriveAchievements(
  backend: BackendEnergyStats | null
): Achievement[] {
  const inferences = backend?.total_inferences ?? 0;
  const energySavedKwh = backend?.savings.energy_saved_kwh ?? 0;
  const costSaved = backend?.savings.cost_saved_usd ?? 0;
  const uptimeHours = (backend?.session_uptime_seconds ?? 0) / 3600;
  const avgMj = backend?.avg_energy_per_token_mj ?? 0;
  const hasLowEnergy = inferences >= 100 && avgMj > 0 && avgMj < 50;

  return [
    {
      id: "first-inference",
      icon: "sparkles",
      title: "First Inference",
      description: "Completed your first local inference",
      unlocked: inferences >= 1,
      progress: Math.min(inferences, 1),
      target: 1,
    },
    {
      id: "energy-saver",
      icon: "battery",
      title: "Energy Saver",
      description: "Saved 1 kWh vs cloud computing",
      unlocked: energySavedKwh >= 1,
      progress: Math.min(Math.round(energySavedKwh * 100) / 100, 1),
      target: 1,
    },
    {
      id: "green-champion",
      icon: "leaf",
      title: "Green AI Champion",
      description: "100 inferences with <50 mJ average",
      unlocked: hasLowEnergy,
      progress: Math.min(inferences, 100),
      target: 100,
    },
    {
      id: "cost-cutter",
      icon: "scissors",
      title: "Cost Cutter",
      description: "Saved $10 vs API pricing",
      unlocked: costSaved >= 10,
      progress: Math.min(Math.round(costSaved * 100) / 100, 10),
      target: 10,
    },
    {
      id: "marathon-runner",
      icon: "timer",
      title: "Marathon Runner",
      description: "24h continuous uptime",
      unlocked: uptimeHours >= 24,
      progress: Math.min(Math.round(uptimeHours * 10) / 10, 24),
      target: 24,
    },
    {
      id: "community-node",
      icon: "users",
      title: "Community Node",
      description: "Helped 10 peers with inference",
      unlocked: false,
      progress: 0,
      target: 10,
    },
  ];
}

export function useEnergy() {
  const [period, setPeriod] = useState<Period>("month");
  const [backend, setBackend] = useState<BackendEnergyStats | null>(null);
  const [history, setHistory] = useState<
    Array<{ timestamp: number; energy_mj: number; tokens: number }>
  >([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchEnergy = useCallback(async () => {
    try {
      const data = await getEnergyStats();
      setBackend(data);

      // Extract recent history from the raw response (available via HTTP)
      const raw = data as unknown as Record<string, unknown>;
      const hist = raw["recent_history"] as
        | Array<{ timestamp: number; energy_mj: number; tokens: number }>
        | undefined;
      if (hist && Array.isArray(hist)) {
        setHistory(hist);
      }
    } catch {
      // Silently fail — keep previous state
    }
  }, []);

  useEffect(() => {
    fetchEnergy();
    intervalRef.current = setInterval(fetchEnergy, 10_000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchEnergy]);

  const chartData = useMemo(() => {
    const all = buildChartData(history);
    if (all.length === 0) return all;
    switch (period) {
      case "today":
        return all.slice(-10);
      case "week":
        return all.slice(-20);
      case "month":
        return all.slice(-50);
      case "all":
        return all;
    }
  }, [history, period]);

  const stats = useMemo((): EnergyStats => {
    if (!backend) {
      return {
        totalEnergyKwh: 0,
        co2AvoidedKg: 0,
        moneySaved: 0,
        cloudComparisonPercent: 0,
        totalTokens: 0,
        avgEnergyPerToken: 0,
        avgTokensPerDay: 0,
      };
    }

    const ariaEnergy = 28; // mJ/token
    const cloudEnergy = 7000; // mJ/token
    const efficiencyPercent = Math.round(
      ((cloudEnergy - ariaEnergy) / cloudEnergy) * 100
    );

    const uptimeDays = Math.max(backend.session_uptime_seconds / 86400, 1);

    return {
      totalEnergyKwh: Math.round(backend.total_energy_kwh * 10000) / 10000,
      co2AvoidedKg:
        Math.round(backend.savings.co2_saved_kg * 100) / 100,
      moneySaved:
        Math.round(backend.savings.cost_saved_usd * 100) / 100,
      cloudComparisonPercent: efficiencyPercent,
      totalTokens: backend.total_tokens_generated,
      avgEnergyPerToken:
        Math.round(backend.avg_energy_per_token_mj * 100) / 100,
      avgTokensPerDay: Math.round(
        backend.total_tokens_generated / uptimeDays
      ),
    };
  }, [backend]);

  const impactMetrics = useMemo(() => {
    const co2Kg = backend?.savings.co2_saved_kg ?? 0;
    return {
      treesEquivalent: Math.round((co2Kg / 21) * 10) / 10,
      smartphoneCharges: Math.round(co2Kg / 0.008),
      carKmAvoided: Math.round((co2Kg / 0.21) * 10) / 10,
    };
  }, [backend]);

  const achievements = useMemo(
    () => deriveAchievements(backend),
    [backend]
  );

  return {
    period,
    setPeriod,
    stats,
    chartData,
    achievements,
    comparisonData: COMPARISON_DATA,
    impactMetrics,
  };
}
