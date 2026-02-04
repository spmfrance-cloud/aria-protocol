import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

const variantStyles = {
  default: {
    border: "border-border/50 hover:border-primary/30",
    glow: "hover:shadow-[0_0_20px_rgba(99,102,241,0.1)]",
    iconBg: "bg-primary-muted",
    iconColor: "text-primary",
    trendUp: "text-success",
    trendDown: "text-error",
  },
  success: {
    border: "border-border/50 hover:border-success/30",
    glow: "hover:shadow-[0_0_20px_rgba(16,185,129,0.1)]",
    iconBg: "bg-success-muted",
    iconColor: "text-success",
    trendUp: "text-success",
    trendDown: "text-error",
  },
  warning: {
    border: "border-border/50 hover:border-warning/30",
    glow: "hover:shadow-[0_0_20px_rgba(245,158,11,0.1)]",
    iconBg: "bg-warning-muted",
    iconColor: "text-warning",
    trendUp: "text-success",
    trendDown: "text-error",
  },
  error: {
    border: "border-border/50 hover:border-error/30",
    glow: "hover:shadow-[0_0_20px_rgba(239,68,68,0.1)]",
    iconBg: "bg-error-muted",
    iconColor: "text-error",
    trendUp: "text-success",
    trendDown: "text-error",
  },
} as const;

type StatCardVariant = keyof typeof variantStyles;

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number | string;
  suffix?: string;
  trend?: {
    value: number;
    label: string;
  };
  variant?: StatCardVariant;
  className?: string;
  children?: React.ReactNode;
}

function useCountUp(target: number, duration: number = 1200): number {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const start = performance.now();
    let raf: number;

    const step = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCurrent(Math.round(eased * target * 10) / 10);

      if (progress < 1) {
        raf = requestAnimationFrame(step);
      }
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return current;
}

export const StatCard: React.FC<StatCardProps> = ({
  icon: Icon,
  label,
  value,
  suffix,
  trend,
  variant = "default",
  className,
  children,
}) => {
  const styles = variantStyles[variant];
  const numericValue = typeof value === "number" ? value : null;
  const animatedValue = useCountUp(numericValue ?? 0);
  const displayValue = numericValue !== null ? animatedValue : value;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      whileHover={{ y: -2 }}
      className={cn(
        "rounded-xl p-5",
        "bg-surface/80 backdrop-blur-md",
        "border transition-all duration-200",
        styles.border,
        styles.glow,
        className
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center",
            styles.iconBg
          )}
        >
          <Icon size={20} className={styles.iconColor} />
        </div>

        {trend && (
          <div
            className={cn(
              "flex items-center gap-1 text-xs font-medium",
              trend.value >= 0 ? styles.trendUp : styles.trendDown
            )}
          >
            <span>{trend.value >= 0 ? "↑" : "↓"}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>

      <p className="text-sm text-text-secondary mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-text-primary">
          {displayValue}
        </span>
        {suffix && (
          <span className="text-sm text-text-secondary">{suffix}</span>
        )}
      </div>

      {trend && (
        <p className="text-xs text-text-secondary/70 mt-1">{trend.label}</p>
      )}

      {children && <div className="mt-3">{children}</div>}
    </motion.div>
  );
};

StatCard.displayName = "StatCard";
