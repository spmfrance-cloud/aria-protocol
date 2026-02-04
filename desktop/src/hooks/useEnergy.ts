import { useState, useMemo, useCallback } from "react";

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

// Seed-based pseudo-random for reproducible mock data
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 49297;
  return x - Math.floor(x);
}

function generateDailyData(): DailyData[] {
  const data: DailyData[] = [];
  const now = new Date();
  const CO2_FACTOR = 0.4; // kg CO2 per kWh
  const ARIA_COST_PER_TOKEN = 0.000002;
  const CLOUD_COST_PER_TOKEN = 0.000015;
  const GPU_COST_PER_TOKEN = 0.0000008;
  const ARIA_MJ_PER_TOKEN = 0.028; // 28 mJ = 0.028 J expressed as mJ for display
  const CLOUD_MJ_PER_TOKEN = 7.0;

  for (let i = 29; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const seed = date.getFullYear() * 10000 + (date.getMonth() + 1) * 100 + date.getDate();

    // Base ~50K tokens/day with realistic variance
    const variance = seededRandom(seed) * 0.6 + 0.7; // 0.7 to 1.3
    const weekday = date.getDay();
    const weekendFactor = weekday === 0 || weekday === 6 ? 0.6 : 1.0;
    const tokens = Math.round(50000 * variance * weekendFactor);

    const energyMj = tokens * ARIA_MJ_PER_TOKEN;
    const energyKwh = (energyMj / 1000) * (1 / 3600); // mJ → kWh
    const cloudEnergyKwh = (tokens * CLOUD_MJ_PER_TOKEN / 1000) * (1 / 3600);

    const costAria = tokens * ARIA_COST_PER_TOKEN;
    const costCloud = tokens * CLOUD_COST_PER_TOKEN;
    const costGpu = tokens * GPU_COST_PER_TOKEN;
    const co2Avoided = (cloudEnergyKwh - energyKwh) * CO2_FACTOR;

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    data.push({
      date: date.toISOString().split("T")[0],
      label: `${monthNames[date.getMonth()]} ${date.getDate()}`,
      tokens,
      energyMj: Math.round(energyMj * 100) / 100,
      energyKwh: Math.round(energyKwh * 10000) / 10000,
      costAria: Math.round(costAria * 1000) / 1000,
      costCloud: Math.round(costCloud * 100) / 100,
      costGpu: Math.round(costGpu * 1000) / 1000,
      co2Avoided: Math.round(co2Avoided * 1000) / 1000,
    });
  }

  return data;
}

const ALL_DATA = generateDailyData();

const ACHIEVEMENTS: Achievement[] = [
  {
    id: "first-inference",
    icon: "sparkles",
    title: "First Inference",
    description: "Completed your first local inference",
    unlocked: true,
    progress: 1,
    target: 1,
  },
  {
    id: "energy-saver",
    icon: "battery",
    title: "Energy Saver",
    description: "Saved 1 kWh vs cloud computing",
    unlocked: true,
    progress: 1,
    target: 1,
  },
  {
    id: "green-champion",
    icon: "leaf",
    title: "Green AI Champion",
    description: "100 inferences with <50mJ average",
    unlocked: true,
    progress: 100,
    target: 100,
  },
  {
    id: "cost-cutter",
    icon: "scissors",
    title: "Cost Cutter",
    description: "Saved $10 vs API pricing",
    unlocked: true,
    progress: 10,
    target: 10,
  },
  {
    id: "marathon-runner",
    icon: "timer",
    title: "Marathon Runner",
    description: "24h continuous uptime",
    unlocked: false,
    progress: 18,
    target: 24,
  },
  {
    id: "community-node",
    icon: "users",
    title: "Community Node",
    description: "Helped 10 peers with inference",
    unlocked: false,
    progress: 3,
    target: 10,
  },
];

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
    label: "GPT-4 / Claude API",
  },
  {
    name: "RTX 4090",
    energyPerToken: 5625,
    costPerToken: 0.0008,
    color: "#f59e0b",
    label: "Local GPU inference",
  },
];

export function useEnergy() {
  const [period, setPeriod] = useState<Period>("month");

  const getFilteredData = useCallback((p: Period): DailyData[] => {
    switch (p) {
      case "today":
        return ALL_DATA.slice(-1);
      case "week":
        return ALL_DATA.slice(-7);
      case "month":
        return ALL_DATA.slice(-30);
      case "all":
        return ALL_DATA;
    }
  }, []);

  const chartData = useMemo(() => getFilteredData(period), [period, getFilteredData]);

  const stats = useMemo((): EnergyStats => {
    const data = getFilteredData(period);
    const totalTokens = data.reduce((sum, d) => sum + d.tokens, 0);
    const totalEnergyKwh = data.reduce((sum, d) => sum + d.energyKwh, 0);
    const totalCloudCost = data.reduce((sum, d) => sum + d.costCloud, 0);
    const totalAriaCost = data.reduce((sum, d) => sum + d.costAria, 0);
    const co2Avoided = data.reduce((sum, d) => sum + d.co2Avoided, 0);
    const moneySaved = totalCloudCost - totalAriaCost;

    // ARIA vs cloud energy efficiency
    const ariaEnergy = 28; // mJ/token
    const cloudEnergy = 7000; // mJ/token
    const efficiencyPercent = Math.round(((cloudEnergy - ariaEnergy) / cloudEnergy) * 100);

    return {
      totalEnergyKwh: Math.round(totalEnergyKwh * 10000) / 10000,
      co2AvoidedKg: Math.round(co2Avoided * 100) / 100,
      moneySaved: Math.round(moneySaved * 100) / 100,
      cloudComparisonPercent: efficiencyPercent,
      totalTokens,
      avgEnergyPerToken: totalTokens > 0 ? Math.round((totalEnergyKwh * 1e9) / totalTokens * 100) / 100 : 0,
      avgTokensPerDay: Math.round(totalTokens / Math.max(data.length, 1)),
    };
  }, [period, getFilteredData]);

  const impactMetrics = useMemo(() => {
    const data = getFilteredData(period);
    const co2Kg = data.reduce((sum, d) => sum + d.co2Avoided, 0);
    return {
      treesEquivalent: Math.round((co2Kg / 21) * 10) / 10, // ~21 kg CO2/tree/year
      smartphoneCharges: Math.round(co2Kg / 0.008), // ~8g CO2 per charge
      carKmAvoided: Math.round((co2Kg / 0.21) * 10) / 10, // ~210g CO2/km
    };
  }, [period, getFilteredData]);

  return {
    period,
    setPeriod,
    stats,
    chartData,
    achievements: ACHIEVEMENTS,
    comparisonData: COMPARISON_DATA,
    impactMetrics,
  };
}
