import React, { useState } from "react";
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { DailyData } from "@/hooks/useEnergy";

type MetricMode = "energy" | "tokens" | "cost";

interface ConsumptionChartProps {
  data: DailyData[];
  className?: string;
}

const metricConfig: Record<MetricMode, { key: keyof DailyData; label: string; suffix: string; format: (v: number) => string }> = {
  energy: {
    key: "energyMj",
    label: "Energy Consumption",
    suffix: "mJ",
    format: (v: number) => `${v.toLocaleString()} mJ`,
  },
  tokens: {
    key: "tokens",
    label: "Tokens Generated",
    suffix: "tokens",
    format: (v: number) => v.toLocaleString(),
  },
  cost: {
    key: "costAria",
    label: "ARIA Cost",
    suffix: "$",
    format: (v: number) => `$${v.toFixed(4)}`,
  },
};

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ value: number; dataKey: string }>;
  label?: string;
  mode: MetricMode;
}> = ({ active, payload, label, mode }) => {
  if (!active || !payload || payload.length === 0) return null;
  const config = metricConfig[mode];

  return (
    <div
      className={cn(
        "px-3 py-2 rounded-lg",
        "bg-surface/95 backdrop-blur-md",
        "border border-border/50",
        "shadow-lg shadow-black/20"
      )}
    >
      <p className="text-xs text-text-secondary mb-0.5">{label}</p>
      <p className="text-sm font-semibold text-emerald-400">
        {config.format(payload[0].value)}
      </p>
    </div>
  );
};

export const ConsumptionChart: React.FC<ConsumptionChartProps> = ({
  data,
  className,
}) => {
  const [mode, setMode] = useState<MetricMode>("energy");
  const config = metricConfig[mode];

  const chartData = data.map((d) => ({
    label: d.label,
    value: d[config.key] as number,
  }));

  const totalValue = chartData.reduce((sum, d) => sum + d.value, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "rounded-xl p-6",
        "bg-surface/80 backdrop-blur-md",
        "border border-border/50",
        "transition-all duration-200",
        "hover:border-emerald-500/20",
        className
      )}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base font-semibold text-text-primary">
            {config.label}
          </h3>
          <p className="text-sm text-text-secondary">
            Total: {config.format(Math.round(totalValue * 100) / 100)}
          </p>
        </div>

        {/* Toggle */}
        <div className="flex items-center gap-1 p-1 rounded-lg bg-background/50 border border-border/50">
          {(Object.keys(metricConfig) as MetricMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200",
                mode === m
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              {m === "energy" ? "Energy (mJ)" : m === "tokens" ? "Tokens" : "Cost ($)"}
            </button>
          ))}
        </div>
      </div>

      <div className="h-[260px] -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="50%" stopColor="#22c55e" stopOpacity={0.1} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="energyLineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="100%" stopColor="#22c55e" />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              stroke="#1e1e2e"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              interval={Math.max(0, Math.floor(chartData.length / 7) - 1)}
            />
            <YAxis
              stroke="#1e1e2e"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={50}
            />
            <Tooltip content={<CustomTooltip mode={mode} />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="url(#energyLineGradient)"
              strokeWidth={2}
              fill="url(#energyGradient)"
              animationDuration={600}
              dot={false}
              activeDot={{
                r: 4,
                fill: "#10b981",
                stroke: "#0a0a0f",
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

ConsumptionChart.displayName = "ConsumptionChart";
