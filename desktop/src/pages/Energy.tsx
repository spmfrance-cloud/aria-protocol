import { motion } from "framer-motion";
import { Zap, Leaf, DollarSign, Cloud } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { EnergySavingsCard } from "@/components/energy/EnergySavingsCard";
import { ConsumptionChart } from "@/components/energy/ConsumptionChart";
import { ComparisonWidget } from "@/components/energy/ComparisonWidget";
import { AchievementsGrid } from "@/components/energy/AchievementsGrid";
import { ImpactSummary } from "@/components/energy/ImpactSummary";
import { useEnergy, type Period } from "@/hooks/useEnergy";
import { cn } from "@/lib/utils";

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

const periods: { value: Period; label: string }[] = [
  { value: "today", label: "Today" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "all", label: "All Time" },
];

export default function Energy() {
  const {
    period,
    setPeriod,
    stats,
    chartData,
    achievements,
    comparisonData,
    impactMetrics,
  } = useEnergy();

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 max-w-[1400px]"
    >
      {/* Header */}
      <motion.header
        variants={item}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
            Energy & Savings
          </h1>
          <p className="text-sm text-text-secondary">
            Track your energy impact and savings from local inference
          </p>
        </div>

        {/* Period selector */}
        <div className="flex items-center gap-1 p-1 rounded-lg bg-surface/80 border border-border/50">
          {periods.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={cn(
                "px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200",
                period === p.value
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </motion.header>

      {/* Stats Grid */}
      <motion.div
        variants={item}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <StatCard
          icon={Zap}
          label="Total Energy Used"
          value={stats.totalEnergyKwh}
          suffix="kWh"
          trend={{ value: -8.2, label: "more efficient" }}
          variant="success"
        />
        <StatCard
          icon={Leaf}
          label="CO₂ Avoided"
          value={stats.co2AvoidedKg}
          suffix="kg"
          trend={{ value: 12.5, label: "vs last period" }}
          variant="success"
        />
        <StatCard
          icon={DollarSign}
          label="Money Saved"
          value={stats.moneySaved}
          suffix="$"
          trend={{ value: 15.3, label: "vs last period" }}
          variant="success"
        />
        <StatCard
          icon={Cloud}
          label="vs Cloud Comparison"
          value={stats.cloudComparisonPercent}
          suffix="%"
          trend={{ value: 0, label: "more efficient than cloud" }}
          variant="success"
        />
      </motion.div>

      {/* Savings Hero Card */}
      <motion.div variants={item}>
        <EnergySavingsCard moneySaved={stats.moneySaved} />
      </motion.div>

      {/* Chart Section */}
      <motion.div variants={item}>
        <ConsumptionChart data={chartData} />
      </motion.div>

      {/* Comparison & Impact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={item}>
          <ComparisonWidget data={comparisonData} />
        </motion.div>
        <motion.div variants={item}>
          <ImpactSummary
            treesEquivalent={impactMetrics.treesEquivalent}
            smartphoneCharges={impactMetrics.smartphoneCharges}
            carKmAvoided={impactMetrics.carKmAvoided}
          />
        </motion.div>
      </div>

      {/* Achievements */}
      <motion.div variants={item}>
        <AchievementsGrid achievements={achievements} />
      </motion.div>
    </motion.div>
  );
}
