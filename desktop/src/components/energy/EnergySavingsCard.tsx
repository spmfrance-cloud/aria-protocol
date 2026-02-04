import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { DollarSign, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface EnergySavingsCardProps {
  moneySaved: number;
  className?: string;
}

function useCountUp(target: number, duration: number = 2000): number {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const start = performance.now();
    let raf: number;

    const step = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic for satisfying deceleration
      const eased = 1 - Math.pow(1 - progress, 3);
      setCurrent(Math.round(eased * target * 100) / 100);

      if (progress < 1) {
        raf = requestAnimationFrame(step);
      }
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return current;
}

export const EnergySavingsCard: React.FC<EnergySavingsCardProps> = ({
  moneySaved,
  className,
}) => {
  const animatedValue = useCountUp(moneySaved, 2200);
  const [showCoins, setShowCoins] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowCoins(true), 800);
    return () => clearTimeout(timer);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={cn(
        "relative rounded-xl p-6 overflow-hidden",
        "bg-gradient-to-br from-emerald-500/10 via-surface/80 to-green-500/5",
        "backdrop-blur-md",
        "border border-emerald-500/20",
        "hover:border-emerald-500/40 transition-all duration-300",
        "hover:shadow-[0_0_30px_rgba(16,185,129,0.1)]",
        className
      )}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: showCoins ? [0, -10, 10, -5, 0] : 0 }}
              transition={{ duration: 0.6, delay: 1.5 }}
              className="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center"
            >
              <DollarSign size={24} className="text-emerald-400" />
            </motion.div>
            <div>
              <h3 className="text-sm font-medium text-text-secondary">Total Savings</h3>
              <p className="text-xs text-emerald-400/80">vs Cloud API pricing</p>
            </div>
          </div>
          <div className="flex items-center gap-1 text-xs font-medium text-emerald-400">
            <TrendingDown size={14} />
            <span>99.9% cheaper</span>
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-4">
          <motion.span
            className="text-4xl font-bold text-text-primary"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5, type: "spring", stiffness: 200 }}
          >
            ${animatedValue.toFixed(2)}
          </motion.span>
          <span className="text-sm text-text-secondary">saved</span>
        </div>

        <p className="text-sm text-text-secondary">
          You saved{" "}
          <span className="text-emerald-400 font-medium">
            ${moneySaved.toFixed(2)}
          </span>{" "}
          vs GPT-4 API costs by running inference locally
        </p>

        {/* Animated coins */}
        {showCoins && (
          <div className="absolute top-4 right-4 pointer-events-none">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                initial={{ y: -20, opacity: 0, x: i * 8 }}
                animate={{ y: [0, 40], opacity: [1, 0] }}
                transition={{
                  delay: 1.8 + i * 0.15,
                  duration: 1.2,
                  ease: "easeIn",
                }}
                className="absolute text-lg"
              >
                💰
              </motion.span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

EnergySavingsCard.displayName = "EnergySavingsCard";
