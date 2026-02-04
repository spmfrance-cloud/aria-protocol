import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ComparisonData } from "@/hooks/useEnergy";

interface ComparisonWidgetProps {
  data: ComparisonData[];
  className?: string;
}

const EnergyBar: React.FC<{
  item: ComparisonData;
  maxEnergy: number;
  maxCost: number;
  index: number;
}> = ({ item, maxEnergy, maxCost, index }) => {
  const energyPercent = (item.energyPerToken / maxEnergy) * 100;
  const costPercent = (item.costPerToken / maxCost) * 100;

  // Efficiency multiplier vs cloud (second item)
  const efficiencyLabel =
    index === 0
      ? `${Math.round(7000 / 28)}x more efficient`
      : index === 2
        ? `${Math.round(7000 / 5625)}x more efficient`
        : "Baseline";

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-sm font-medium text-text-primary">{item.name}</span>
        </div>
        <span className="text-xs text-text-secondary">{item.label}</span>
      </div>

      {/* Energy bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-text-secondary">Energy</span>
          <span className="text-text-primary font-mono">
            {item.energyPerToken.toLocaleString()} mJ/token
          </span>
        </div>
        <div className="h-3 rounded-full bg-background/50 border border-border/30 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.max(energyPercent, 1)}%` }}
            transition={{ delay: 0.3 + index * 0.15, duration: 0.8, ease: "easeOut" }}
            className="h-full rounded-full"
            style={{ backgroundColor: item.color }}
          />
        </div>
      </div>

      {/* Cost bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-text-secondary">Cost</span>
          <span className="text-text-primary font-mono">
            ${item.costPerToken < 0.001
              ? item.costPerToken.toExponential(1)
              : item.costPerToken.toFixed(4)}/token
          </span>
        </div>
        <div className="h-3 rounded-full bg-background/50 border border-border/30 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.max(costPercent, 1)}%` }}
            transition={{ delay: 0.5 + index * 0.15, duration: 0.8, ease: "easeOut" }}
            className="h-full rounded-full"
            style={{ backgroundColor: item.color, opacity: 0.7 }}
          />
        </div>
      </div>

      {/* Efficiency label */}
      <div className="flex justify-end">
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full",
            index === 0
              ? "bg-emerald-500/15 text-emerald-400"
              : index === 2
                ? "bg-amber-500/15 text-amber-400"
                : "bg-primary-muted text-primary"
          )}
        >
          {efficiencyLabel}
        </span>
      </div>
    </div>
  );
};

export const ComparisonWidget: React.FC<ComparisonWidgetProps> = ({
  data,
  className,
}) => {
  const maxEnergy = Math.max(...data.map((d) => d.energyPerToken));
  const maxCost = Math.max(...data.map((d) => d.costPerToken));

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
      <div className="mb-6">
        <h3 className="text-base font-semibold text-text-primary">
          ARIA vs Cloud vs GPU
        </h3>
        <p className="text-sm text-text-secondary">
          Energy and cost comparison per token
        </p>
      </div>

      <div className="space-y-6">
        {data.map((item, index) => (
          <EnergyBar
            key={item.name}
            item={item}
            maxEnergy={maxEnergy}
            maxCost={maxCost}
            index={index}
          />
        ))}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="mt-6 pt-4 border-t border-border/50"
      >
        <p className="text-sm text-text-secondary text-center">
          ARIA is{" "}
          <span className="text-emerald-400 font-semibold">250x cheaper</span>
          {" "}and{" "}
          <span className="text-emerald-400 font-semibold">250x more energy efficient</span>
          {" "}than cloud APIs
        </p>
      </motion.div>
    </motion.div>
  );
};

ComparisonWidget.displayName = "ComparisonWidget";
