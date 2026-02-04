import { motion, AnimatePresence } from "framer-motion";
import { Activity, Clock, Zap } from "lucide-react";
import type { GenerationStats } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

interface ChatStatsProps {
  stats: GenerationStats;
  isGenerating: boolean;
  className?: string;
}

export const ChatStats: React.FC<ChatStatsProps> = ({
  stats,
  isGenerating,
  className,
}) => {
  return (
    <AnimatePresence>
      {isGenerating && stats.tokensGenerated > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -8, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className={cn(
            "flex items-center gap-4",
            "px-3 py-1.5 rounded-lg",
            "bg-surface/80 backdrop-blur-md border border-border/50",
            "text-xs text-text-secondary",
            className
          )}
        >
          <div className="flex items-center gap-1.5">
            <Zap size={12} className="text-accent" />
            <span className="tabular-nums font-mono">
              {stats.tokensGenerated} tokens
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <Activity size={12} className="text-primary" />
            <span className="tabular-nums font-mono">
              {stats.tokensPerSecond} t/s
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <Clock size={12} className="text-text-secondary/60" />
            <span className="tabular-nums font-mono">
              {(stats.elapsedMs / 1000).toFixed(1)}s
            </span>
          </div>

          {/* Pulsing dot */}
          <motion.div
            className="w-1.5 h-1.5 rounded-full bg-success"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

ChatStats.displayName = "ChatStats";
