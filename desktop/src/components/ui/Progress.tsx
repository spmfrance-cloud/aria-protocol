import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const colorMap = {
  primary: {
    bar: "bg-primary",
    glow: "shadow-[0_0_10px_rgba(99,102,241,0.4)]",
  },
  accent: {
    bar: "bg-accent",
    glow: "shadow-[0_0_10px_rgba(34,211,238,0.4)]",
  },
  success: {
    bar: "bg-success",
    glow: "shadow-[0_0_10px_rgba(16,185,129,0.4)]",
  },
  warning: {
    bar: "bg-warning",
    glow: "shadow-[0_0_10px_rgba(245,158,11,0.4)]",
  },
  error: {
    bar: "bg-error",
    glow: "shadow-[0_0_10px_rgba(239,68,68,0.4)]",
  },
} as const;

type ProgressColor = keyof typeof colorMap;

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  color?: ProgressColor;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "h-1",
  md: "h-2",
  lg: "h-3",
};

export const Progress: React.FC<ProgressProps> = ({
  className,
  value,
  max = 100,
  color = "primary",
  showLabel = false,
  size = "md",
  ...props
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const { bar, glow } = colorMap[color];

  return (
    <div className={cn("space-y-1.5", className)} {...props}>
      {showLabel && (
        <div className="flex justify-between items-center">
          <span className="text-xs text-text-secondary">Progress</span>
          <span className="text-xs font-mono text-text-primary">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      <div
        className={cn(
          "w-full rounded-full overflow-hidden",
          "bg-border/50",
          sizeClasses[size]
        )}
      >
        <motion.div
          className={cn("h-full rounded-full", bar, glow)}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
};

Progress.displayName = "Progress";
