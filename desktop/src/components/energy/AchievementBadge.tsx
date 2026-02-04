import React from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  BatteryFull,
  Leaf,
  Scissors,
  Timer,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

const iconMap: Record<string, LucideIcon> = {
  sparkles: Sparkles,
  battery: BatteryFull,
  leaf: Leaf,
  scissors: Scissors,
  timer: Timer,
  users: Users,
};

interface AchievementBadgeProps {
  icon: string;
  title: string;
  description: string;
  unlocked: boolean;
  progress: number;
  target: number;
  className?: string;
}

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  icon,
  title,
  description,
  unlocked,
  progress,
  target,
  className,
}) => {
  const Icon = iconMap[icon] || Sparkles;
  const progressPercent = Math.min((progress / target) * 100, 100);

  return (
    <motion.div
      whileHover={{ scale: unlocked ? 1.03 : 1.01 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "relative rounded-xl p-4",
        "border transition-all duration-300",
        unlocked
          ? "bg-surface/80 border-emerald-500/30 hover:border-emerald-500/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.1)]"
          : "bg-surface/40 border-border/30 opacity-60",
        className
      )}
    >
      {/* Unlocked glow */}
      {unlocked && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none" />
      )}

      <div className="relative z-10 flex items-start gap-3">
        <motion.div
          initial={unlocked ? { scale: 0 } : { scale: 1 }}
          animate={{ scale: 1 }}
          transition={unlocked ? { type: "spring", stiffness: 300, damping: 15, delay: 0.2 } : {}}
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
            unlocked
              ? "bg-emerald-500/15"
              : "bg-border/30"
          )}
        >
          <Icon
            size={20}
            className={cn(
              unlocked ? "text-emerald-400" : "text-text-secondary/50"
            )}
          />
        </motion.div>

        <div className="flex-1 min-w-0">
          <h4
            className={cn(
              "text-sm font-medium truncate",
              unlocked ? "text-text-primary" : "text-text-secondary/60"
            )}
          >
            {title}
          </h4>
          <p
            className={cn(
              "text-xs mt-0.5",
              unlocked ? "text-text-secondary" : "text-text-secondary/40"
            )}
          >
            {description}
          </p>

          {/* Progress bar for locked achievements */}
          {!unlocked && (
            <div className="mt-2 space-y-1">
              <div className="h-1.5 rounded-full bg-background/50 border border-border/20 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                  className="h-full rounded-full bg-text-secondary/30"
                />
              </div>
              <p className="text-xs text-text-secondary/40">
                {progress}/{target}
              </p>
            </div>
          )}

          {unlocked && (
            <div className="mt-1.5 flex items-center gap-1">
              <span className="text-xs text-emerald-400 font-medium">Unlocked</span>
              <span className="text-emerald-400 text-xs">✓</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

AchievementBadge.displayName = "AchievementBadge";
