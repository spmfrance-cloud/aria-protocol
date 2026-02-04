import React from "react";
import { motion } from "framer-motion";
import { TreePine, Smartphone, Car } from "lucide-react";
import { cn } from "@/lib/utils";

interface ImpactSummaryProps {
  treesEquivalent: number;
  smartphoneCharges: number;
  carKmAvoided: number;
  className?: string;
}

const impactItems = [
  {
    key: "trees" as const,
    icon: TreePine,
    labelFn: (v: number) => `${v} trees planted`,
    description: "Equivalent CO₂ absorption",
    color: "text-emerald-400",
    bg: "bg-emerald-500/15",
  },
  {
    key: "phones" as const,
    icon: Smartphone,
    labelFn: (v: number) => `${v.toLocaleString()} smartphone charges`,
    description: "Energy equivalent saved",
    color: "text-sky-400",
    bg: "bg-sky-500/15",
  },
  {
    key: "car" as const,
    icon: Car,
    labelFn: (v: number) => `${v} km of driving`,
    description: "Car emissions avoided",
    color: "text-amber-400",
    bg: "bg-amber-500/15",
  },
];

export const ImpactSummary: React.FC<ImpactSummaryProps> = ({
  treesEquivalent,
  smartphoneCharges,
  carKmAvoided,
  className,
}) => {
  const values = {
    trees: treesEquivalent,
    phones: smartphoneCharges,
    car: carKmAvoided,
  };

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
      <div className="mb-5">
        <h3 className="text-base font-semibold text-text-primary">
          Your Environmental Impact
        </h3>
        <p className="text-sm text-text-secondary">
          Real-world equivalents of your savings
        </p>
      </div>

      <div className="space-y-4">
        {impactItems.map(({ key, icon: Icon, labelFn, description, color, bg }, index) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + index * 0.1, duration: 0.4, ease: "easeOut" }}
            className="flex items-center gap-4 p-3 rounded-lg bg-background/30 border border-border/20"
          >
            <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0", bg)}>
              <Icon size={20} className={color} />
            </div>
            <div className="flex-1 min-w-0">
              <p className={cn("text-sm font-semibold", color)}>
                {labelFn(values[key])}
              </p>
              <p className="text-xs text-text-secondary">{description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

ImpactSummary.displayName = "ImpactSummary";
