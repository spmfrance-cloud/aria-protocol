import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Power, Square, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui";
import { useBackend } from "@/hooks/useBackend";
import { startNode, stopNode } from "@/lib/tauri";

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
  const { nodeRunning, uptime, backend, refresh } = useBackend();
  const [displayUptime, setDisplayUptime] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Keep local uptime ticking when backend is running
  useEffect(() => {
    setDisplayUptime(uptime);
  }, [uptime]);

  useEffect(() => {
    if (!nodeRunning) return;
    const interval = setInterval(() => {
      setDisplayUptime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [nodeRunning]);

  const handleToggle = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (nodeRunning) {
        await stopNode();
      } else {
        await startNode();
      }
      // Wait briefly then refresh status
      setTimeout(() => {
        refresh();
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      setError(String(err));
      setIsLoading(false);
    }
  }, [nodeRunning, refresh]);

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
        nodeRunning
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
                nodeRunning ? "bg-success" : "bg-error"
              )}
            />
            {nodeRunning && (
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-success animate-ping opacity-40" />
            )}
          </div>
          <span
            className={cn(
              "text-xs font-semibold",
              nodeRunning ? "text-success" : "text-error"
            )}
          >
            {nodeRunning ? "Online" : "Offline"}
          </span>
        </div>
      </div>

      {/* Uptime */}
      <div className="mb-2">
        <p className="text-xs text-text-secondary/70 mb-1">Uptime</p>
        <p className="text-xl font-mono font-bold text-text-primary">
          {nodeRunning ? formatUptime(displayUptime) : "--:--:--"}
        </p>
      </div>

      {/* Backend type */}
      {nodeRunning && (
        <p className="text-[10px] text-text-secondary/50 mb-3">
          Backend: {backend}
        </p>
      )}

      {/* Error message */}
      {error && (
        <p className="text-[10px] text-error mb-2 line-clamp-2">{error}</p>
      )}

      {/* Toggle button */}
      <Button
        variant={nodeRunning ? "danger" : "primary"}
        size="sm"
        className="w-full"
        onClick={handleToggle}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            {nodeRunning ? "Stopping..." : "Starting..."}
          </>
        ) : nodeRunning ? (
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
