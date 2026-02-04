import React from "react";
import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ModelInfo } from "@/hooks/useModels";

interface ModelStatsProps {
  models: ModelInfo[];
  className?: string;
}

const maxPerf = 100; // Normalize performance bar to this max
const maxSize = 5; // Normalize size bar to this max (GB)

function parsePerformance(perf: string): number {
  return parseFloat(perf.replace(" t/s", ""));
}

function parseSize(size: string): number {
  const val = parseFloat(size);
  if (size.includes("MB")) return val / 1000;
  return val; // GB
}

export const ModelStats: React.FC<ModelStatsProps> = ({
  models,
  className,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className={cn(
        "rounded-xl p-5",
        "bg-surface/80 backdrop-blur-md",
        "border border-border/50",
        className
      )}
    >
      <div className="flex items-center gap-2 mb-5">
        <div className="w-8 h-8 rounded-lg bg-accent-muted flex items-center justify-center">
          <BarChart3 size={16} className="text-accent" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-text-primary">
            Model Comparison
          </h3>
          <p className="text-xs text-text-secondary">
            Performance vs Size
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {models.map((model, index) => {
          const perf = parsePerformance(model.performance);
          const size = parseSize(model.size);
          const perfPercent = Math.min((perf / maxPerf) * 100, 100);
          const sizePercent = Math.min((size / maxSize) * 100, 100);

          return (
            <div key={model.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-text-primary truncate max-w-[140px]">
                  {model.name}
                </span>
                <span className="text-[10px] text-text-secondary font-mono">
                  {model.params}
                </span>
              </div>

              {/* Performance bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-text-secondary uppercase tracking-wider">
                    Speed
                  </span>
                  <span className="text-[10px] font-mono text-text-secondary">
                    {model.performance}
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-border/50 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${perfPercent}%` }}
                    transition={{
                      duration: 0.8,
                      delay: index * 0.15,
                      ease: "easeOut",
                    }}
                    className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                  />
                </div>
              </div>

              {/* Size bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-text-secondary uppercase tracking-wider">
                    RAM
                  </span>
                  <span className="text-[10px] font-mono text-text-secondary">
                    {model.ram}
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-border/50 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${sizePercent}%` }}
                    transition={{
                      duration: 0.8,
                      delay: index * 0.15 + 0.1,
                      ease: "easeOut",
                    }}
                    className="h-full rounded-full bg-gradient-to-r from-warning/80 to-error/60"
                  />
                </div>
              </div>

              {index < models.length - 1 && (
                <div className="border-b border-border/30 pt-1" />
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-border/30">
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-sm bg-gradient-to-r from-primary to-accent" />
          <span className="text-[10px] text-text-secondary">
            Speed (higher = better)
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-sm bg-gradient-to-r from-warning/80 to-error/60" />
          <span className="text-[10px] text-text-secondary">
            RAM (lower = lighter)
          </span>
        </div>
      </div>
    </motion.div>
  );
};

ModelStats.displayName = "ModelStats";
