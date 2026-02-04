import React from "react";
import { motion } from "framer-motion";
import { Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import { AchievementBadge } from "./AchievementBadge";
import type { Achievement } from "@/hooks/useEnergy";

interface AchievementsGridProps {
  achievements: Achievement[];
  className?: string;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const item = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3, ease: "easeOut" } },
};

export const AchievementsGrid: React.FC<AchievementsGridProps> = ({
  achievements,
  className,
}) => {
  const unlockedCount = achievements.filter((a) => a.unlocked).length;
  const totalCount = achievements.length;

  // Find next locked achievement for progress
  const nextLocked = achievements.find((a) => !a.unlocked);
  const overallProgress = (unlockedCount / totalCount) * 100;

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
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-500/15 flex items-center justify-center">
            <Trophy size={20} className="text-amber-400" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-text-primary">
              Achievements
            </h3>
            <p className="text-sm text-text-secondary">
              {unlockedCount}/{totalCount} unlocked
            </p>
          </div>
        </div>
      </div>

      {/* Overall progress bar */}
      <div className="mb-5 space-y-2">
        <div className="h-2 rounded-full bg-background/50 border border-border/30 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-400"
          />
        </div>
        {nextLocked && (
          <p className="text-xs text-text-secondary">
            Next: <span className="text-text-primary">{nextLocked.title}</span>
            {" — "}
            {nextLocked.progress}/{nextLocked.target}
          </p>
        )}
      </div>

      {/* Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 gap-3"
      >
        {achievements.map((achievement) => (
          <motion.div key={achievement.id} variants={item}>
            <AchievementBadge
              icon={achievement.icon}
              title={achievement.title}
              description={achievement.description}
              unlocked={achievement.unlocked}
              progress={achievement.progress}
              target={achievement.target}
            />
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
};

AchievementsGrid.displayName = "AchievementsGrid";
