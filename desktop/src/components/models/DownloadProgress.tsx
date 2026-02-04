import React from "react";
import { motion } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DownloadProgressProps {
  progress: number;
  speed: string;
  eta: string;
  onCancel: () => void;
  className?: string;
}

export const DownloadProgress: React.FC<DownloadProgressProps> = ({
  progress,
  speed,
  eta,
  onCancel,
  className,
}) => {
  return (
    <div className={cn("space-y-2", className)}>
      {/* Progress bar */}
      <div className="relative w-full h-2 rounded-full overflow-hidden bg-border/50">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            background:
              "linear-gradient(90deg, #6366f1, #22d3ee, #6366f1)",
            backgroundSize: "200% 100%",
          }}
          initial={{ width: 0 }}
          animate={{
            width: `${progress}%`,
            backgroundPosition: ["0% 0%", "100% 0%"],
          }}
          transition={{
            width: { duration: 0.3, ease: "easeOut" },
            backgroundPosition: {
              duration: 2,
              ease: "linear",
              repeat: Infinity,
            },
          }}
        />
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full opacity-50"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
            backgroundSize: "50% 100%",
          }}
          animate={{
            backgroundPosition: ["0% 0%", "200% 0%"],
          }}
          transition={{
            duration: 1.5,
            ease: "linear",
            repeat: Infinity,
          }}
        />
      </div>

      {/* Info row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-medium text-text-primary">
            {progress}%
          </span>
          {speed && (
            <span className="text-xs text-text-secondary">{speed}</span>
          )}
          {eta && (
            <span className="text-xs text-text-secondary/70">{eta}</span>
          )}
        </div>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation();
            onCancel();
          }}
          className="p-1 rounded-md text-text-secondary hover:text-error hover:bg-error-muted transition-colors"
          title="Cancel download"
        >
          <X size={14} />
        </motion.button>
      </div>
    </div>
  );
};

DownloadProgress.displayName = "DownloadProgress";
