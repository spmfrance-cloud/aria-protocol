import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import {
  Activity,
  Zap,
  Users,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { format } from "date-fns";
import { StatCard } from "@/components/dashboard/StatCard";
import { PerformanceChart } from "@/components/dashboard/PerformanceChart";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { NodeStatus } from "@/components/dashboard/NodeStatus";
import { BackendBadge } from "@/components/dashboard/BackendBadge";
import { useBackend } from "@/hooks/useBackend";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

export default function Dashboard() {
  const { t } = useTranslation();
  const { mode, nodeRunning } = useBackend();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 max-w-[1400px]"
    >
      {/* Header */}
      <motion.header variants={item} className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-text-primary">
            {t("dashboard.welcome")}
          </h1>
          <p className="text-sm text-text-secondary">
            {format(currentTime, "EEEE, MMMM d, yyyy")} —{" "}
            <span className="font-mono">{format(currentTime, "HH:mm:ss")}</span>
          </p>
        </div>
        <BackendBadge />
      </motion.header>

      {/* Offline banner */}
      {!nodeRunning && mode !== "mock" && (
        <motion.div
          variants={item}
          className="flex items-center gap-3 p-4 rounded-xl bg-warning/10 border border-warning/20"
        >
          <AlertCircle size={20} className="text-warning flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-text-primary">
              Start your node to see live metrics
            </p>
            <p className="text-xs text-text-secondary mt-0.5">
              Click "Start Node" below to launch the ARIA backend and enable real-time inference.
            </p>
          </div>
        </motion.div>
      )}

      {/* Stats Grid */}
      <motion.div
        variants={item}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <NodeStatus />

        <StatCard
          icon={Activity}
          label={t("dashboard.tokensPerSec")}
          value={nodeRunning ? 0 : 0}
          suffix="tok/s"
          trend={nodeRunning ? { value: 0, label: "ready" } : undefined}
          variant="default"
        >
          {nodeRunning ? (
            <div className="flex items-end gap-[2px] h-8 mt-1">
              {[35, 42, 38, 55, 48, 62, 57, 71, 65, 58, 72, 68, 75, 62, 58].map(
                (v, i) => (
                  <motion.div
                    key={i}
                    initial={{ height: 0 }}
                    animate={{ height: `${(v / 80) * 100}%` }}
                    transition={{ delay: i * 0.04, duration: 0.4 }}
                    className="flex-1 rounded-sm bg-gradient-to-t from-primary/40 to-accent/60"
                  />
                )
              )}
            </div>
          ) : (
            <p className="text-xs text-text-secondary/50 mt-2">
              Start node for live data
            </p>
          )}
        </StatCard>

        <StatCard
          icon={Zap}
          label={t("dashboard.energyUsage")}
          value={nodeRunning ? 0 : 0}
          suffix="mJ/token"
          trend={
            nodeRunning
              ? { value: 0, label: t("energy.moreEfficient") }
              : undefined
          }
          variant="success"
        >
          {nodeRunning ? (
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp size={12} className="text-success" />
              <span className="text-xs text-success">Optimized</span>
            </div>
          ) : (
            <p className="text-xs text-text-secondary/50 mt-2">
              Start node for live data
            </p>
          )}
        </StatCard>

        <StatCard
          icon={Users}
          label={t("dashboard.peersConnected")}
          value={nodeRunning ? 1 : 0}
          trend={nodeRunning ? { value: 0, label: "local node" } : undefined}
          variant="default"
        />
      </motion.div>

      {/* Charts & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <motion.div variants={item} className="lg:col-span-3">
          <PerformanceChart />
        </motion.div>

        <motion.div variants={item} className="lg:col-span-2">
          <ActivityFeed />
        </motion.div>
      </div>
    </motion.div>
  );
}
