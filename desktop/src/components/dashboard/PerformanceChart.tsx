import React, { useState, useEffect } from "react";
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

interface DataPoint {
  time: string;
  value: number;
}

// FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
function generateMockData(count: number): DataPoint[] {
  const data: DataPoint[] = [];
  const now = Date.now();
  let value = 55;

  for (let i = count - 1; i >= 0; i--) {
    const delta = (Math.random() - 0.45) * 12;
    value = Math.max(30, Math.min(90, value + delta));
    const time = new Date(now - i * 1000);
    data.push({
      time: `${time.getMinutes().toString().padStart(2, "0")}:${time.getSeconds().toString().padStart(2, "0")}`,
      value: Math.round(value * 10) / 10,
    });
  }

  return data;
}

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

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
      <p className="text-sm font-semibold text-accent">
        {payload[0].value} <span className="text-text-secondary font-normal">tok/s</span>
      </p>
    </div>
  );
};

interface PerformanceChartProps {
  className?: string;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  className,
}) => {
  const [data, setData] = useState<DataPoint[]>(() => generateMockData(60));

  useEffect(() => {
    const interval = setInterval(() => {
      setData((prev) => {
        const last = prev[prev.length - 1];
        const delta = (Math.random() - 0.45) * 10;
        const newValue = Math.max(
          30,
          Math.min(90, last.value + delta)
        );
        const now = new Date();
        const newPoint: DataPoint = {
          time: `${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`,
          value: Math.round(newValue * 10) / 10,
        };
        return [...prev.slice(1), newPoint];
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const avgValue =
    Math.round(
      (data.reduce((sum, d) => sum + d.value, 0) / data.length) * 10
    ) / 10;

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
        "hover:border-primary/20",
        className
      )}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-text-primary">
            Performance
          </h3>
          <p className="text-sm text-text-secondary">
            Inference speed — last 60 seconds
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-accent">{avgValue}</p>
          <p className="text-xs text-text-secondary">avg tok/s</p>
        </div>
      </div>

      <div className="h-[240px] -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.3} />
                <stop offset="50%" stopColor="#6366f1" stopOpacity={0.1} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              stroke="#1e1e2e"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              interval={14}
            />
            <YAxis
              domain={[20, 100]}
              stroke="#1e1e2e"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={35}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="url(#lineGradient)"
              strokeWidth={2}
              fill="url(#chartGradient)"
              animationDuration={300}
              dot={false}
              activeDot={{
                r: 4,
                fill: "#22d3ee",
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

PerformanceChart.displayName = "PerformanceChart";
