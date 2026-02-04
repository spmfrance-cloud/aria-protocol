import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Power, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui";

interface NodeStatusProps {
  className?: string;
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export const NodeStatus: React.FC<NodeStatusProps> = ({ className }) => {
  const [online, setOnline] = useState(true);
  const [uptime, setUptime] = useState(3742);

  useEffect(() => {
    if (!online) return;

    const interval = setInterval(() => {
      setUptime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [online]);

  const handleToggle = () => {
    if (online) {
      setOnline(false);
    } else {
      setOnline(true);
      setUptime(0);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "rounded-xl p-5",
        "bg-surface/80 backdrop-blur-md",
        "border border-border/50",
        "transition-all duration-200",
        online
          ? "hover:border-success/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.08)]"
          : "hover:border-error/30 hover:shadow-[0_0_20px_rgba(239,68,68,0.08)]",
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-text-secondary">Node Status</p>

        {/* Status badge with pulse */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <div
              className={cn(
                "w-2.5 h-2.5 rounded-full",
                online ? "bg-success" : "bg-error"
              )}
            />
            {online && (
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-success animate-ping opacity-40" />
            )}
          </div>
          <span
            className={cn(
              "text-xs font-semibold",
              online ? "text-success" : "text-error"
            )}
          >
            {online ? "Online" : "Offline"}
          </span>
        </div>
      </div>

      {/* Uptime */}
      <div className="mb-4">
        <p className="text-xs text-text-secondary/70 mb-1">Uptime</p>
        <p className="text-xl font-mono font-bold text-text-primary">
          {formatUptime(uptime)}
        </p>
      </div>

      {/* Toggle button */}
      <Button
        variant={online ? "danger" : "primary"}
        size="sm"
        className="w-full"
        onClick={handleToggle}
      >
        {online ? (
          <>
            <Square size={14} /> Stop Node
          </>
        ) : (
          <>
            <Power size={14} /> Start Node
          </>
        )}
      </Button>
    </motion.div>
  );
};

NodeStatus.displayName = "NodeStatus";
