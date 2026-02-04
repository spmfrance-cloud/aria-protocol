import React from "react";
import { motion } from "framer-motion";
import { MessageSquare, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

interface ActivityItem {
  id: string;
  timestamp: Date;
  prompt: string;
  tokens: number;
  duration: number;
}

function generateMockActivity(): ActivityItem[] {
  const prompts = [
    "Explain the concept of 1-bit quantization in neural networks",
    "Write a Python function to compute matrix multiplication",
    "What are the benefits of decentralized AI inference?",
    "Summarize the latest research on energy-efficient LLMs",
    "Generate a Rust struct for a peer-to-peer node configuration",
    "How does BitNet reduce memory usage compared to FP16?",
    "Create a TypeScript interface for a WebSocket message protocol",
    "Describe the architecture of a mixture-of-experts model",
    "What is federated learning and how does it preserve privacy?",
    "Write unit tests for the token streaming endpoint",
  ];

  const now = Date.now();
  return prompts.map((prompt, i) => ({
    id: `activity-${i}`,
    timestamp: new Date(now - i * 47000 - Math.random() * 30000),
    prompt,
    tokens: Math.floor(Math.random() * 400) + 50,
    duration: Math.round((Math.random() * 4 + 0.5) * 100) / 100,
  }));
}

const mockActivity = generateMockActivity();

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const item = {
  hidden: { opacity: 0, x: -8 },
  show: { opacity: 1, x: 0, transition: { duration: 0.3, ease: "easeOut" } },
};

interface ActivityFeedProps {
  className?: string;
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ className }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "rounded-xl",
        "bg-surface/80 backdrop-blur-md",
        "border border-border/50",
        "transition-all duration-200",
        "hover:border-primary/20",
        className
      )}
    >
      <div className="px-6 py-4 border-b border-border/50">
        <h3 className="text-base font-semibold text-text-primary">
          Recent Activity
        </h3>
        <p className="text-sm text-text-secondary">Latest inference requests</p>
      </div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="divide-y divide-border/30 max-h-[400px] overflow-y-auto"
      >
        {mockActivity.map((activity) => (
          <motion.div
            key={activity.id}
            variants={item}
            className="px-6 py-3.5 hover:bg-surface/50 transition-colors duration-150"
          >
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary-muted flex items-center justify-center flex-shrink-0 mt-0.5">
                <MessageSquare size={14} className="text-primary" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary truncate leading-relaxed">
                  {activity.prompt}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-text-secondary/70 flex items-center gap-1">
                    <Clock size={10} />
                    {formatDistanceToNow(activity.timestamp, {
                      addSuffix: true,
                    })}
                  </span>
                  <span className="text-xs font-mono text-accent">
                    {activity.tokens} tokens
                  </span>
                  <span className="text-xs font-mono text-text-secondary">
                    {activity.duration}s
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
};

ActivityFeed.displayName = "ActivityFeed";
