import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useBackend } from "@/hooks/useBackend";

interface BackendBadgeProps {
  compact?: boolean;
  className?: string;
}

export const BackendBadge: React.FC<BackendBadgeProps> = ({
  compact = false,
  className,
}) => {
  const { mode, backend } = useBackend();

  const config = {
    live: {
      dotColor: backend === "native" ? "bg-emerald-400" : "bg-yellow-400",
      textColor: backend === "native" ? "text-emerald-400" : "text-yellow-400",
      borderColor:
        backend === "native" ? "border-emerald-500/30" : "border-yellow-500/30",
      bgColor:
        backend === "native"
          ? "bg-emerald-500/10"
          : "bg-yellow-500/10",
      label: backend === "native" ? "Live — Native" : "Live — Simulation",
      shortLabel: "Live",
    },
    mock: {
      dotColor: "bg-yellow-400",
      textColor: "text-yellow-400",
      borderColor: "border-yellow-500/30",
      bgColor: "bg-yellow-500/10",
      label: "Dev Mode",
      shortLabel: "Mock",
    },
    offline: {
      dotColor: "bg-red-400",
      textColor: "text-red-400",
      borderColor: "border-red-500/30",
      bgColor: "bg-red-500/10",
      label: "Offline",
      shortLabel: "Off",
    },
  };

  const c = config[mode];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "inline-flex items-center gap-1.5",
        "px-2.5 py-1 rounded-full",
        "text-xs font-medium",
        "border backdrop-blur-sm",
        c.bgColor,
        c.borderColor,
        c.textColor,
        className
      )}
    >
      <div className="relative">
        <div className={cn("w-2 h-2 rounded-full", c.dotColor)} />
        {mode === "live" && (
          <div
            className={cn(
              "absolute inset-0 w-2 h-2 rounded-full animate-ping opacity-40",
              c.dotColor
            )}
          />
        )}
      </div>
      {!compact && <span>{c.label}</span>}
      {compact && <span>{c.shortLabel}</span>}
    </motion.div>
  );
};

BackendBadge.displayName = "BackendBadge";
