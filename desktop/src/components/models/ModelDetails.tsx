import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Download,
  Trash2,
  ExternalLink,
  FolderOpen,
  Gauge,
  Clock,
  Zap,
  HardDrive,
  Cpu,
  Star,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { DownloadProgress } from "./DownloadProgress";
import type { ModelInfo, ModelState } from "@/hooks/useModels";

interface ModelDetailsProps {
  model: ModelInfo | null;
  state: ModelState | null;
  onClose: () => void;
  onDownload: () => void;
  onCancel: () => void;
  onRemove: () => void;
}

const backdrop = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const panel = {
  hidden: { opacity: 0, x: 40, scale: 0.98 },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: { type: "spring", stiffness: 300, damping: 30 },
  },
  exit: {
    opacity: 0,
    x: 40,
    scale: 0.98,
    transition: { duration: 0.2 },
  },
};

export const ModelDetails: React.FC<ModelDetailsProps> = ({
  model,
  state,
  onClose,
  onDownload,
  onCancel,
  onRemove,
}) => {
  if (!model || !state) return null;

  const isDownloading = state.status === "downloading";
  const isInstalled = state.status === "installed";

  return (
    <AnimatePresence>
      {model && (
        <>
          {/* Backdrop */}
          <motion.div
            variants={backdrop}
            initial="hidden"
            animate="visible"
            exit="hidden"
            className="fixed inset-0 z-50 bg-background/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            variants={panel}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={cn(
              "fixed right-0 top-0 bottom-0 z-50",
              "w-full max-w-lg",
              "bg-surface/95 backdrop-blur-xl",
              "border-l border-border/50",
              "flex flex-col",
              "overflow-y-auto"
            )}
          >
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-border/50">
              <div className="flex items-start gap-4">
                <div
                  className={cn(
                    "w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0",
                    isInstalled
                      ? "bg-success-muted"
                      : "bg-gradient-to-br from-primary/20 to-accent/20"
                  )}
                >
                  {isInstalled ? (
                    <CheckCircle2 size={28} className="text-success" />
                  ) : (
                    <Cpu size={28} className="text-primary" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-bold text-text-primary">
                      {model.name}
                    </h2>
                    {model.recommended && (
                      <Badge variant="warning">
                        <Star size={10} className="fill-current" />
                        Recommended
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-text-secondary mt-0.5">
                    {model.params} parameters
                  </p>
                  {isInstalled && (
                    <Badge variant="success" className="mt-2">
                      <CheckCircle2 size={10} />
                      Installed
                    </Badge>
                  )}
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
              >
                <X size={18} />
              </motion.button>
            </div>

            {/* Content */}
            <div className="flex-1 p-6 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">
                  Description
                </h3>
                <p className="text-sm text-text-primary leading-relaxed">
                  {model.description}
                </p>
              </div>

              {/* Benchmarks */}
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-3">
                  Benchmarks
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  <BenchmarkItem
                    icon={Gauge}
                    label="Tokens/s"
                    value={`${model.benchmarks.tokensPerSec}`}
                    unit="t/s"
                  />
                  <BenchmarkItem
                    icon={Clock}
                    label="TTFT"
                    value={model.benchmarks.ttft}
                  />
                  <BenchmarkItem
                    icon={Zap}
                    label="Energy"
                    value={model.benchmarks.energy}
                  />
                </div>
              </div>

              {/* Requirements */}
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-3">
                  Requirements
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-surface/50 border border-border/30">
                    <Cpu size={16} className="text-accent" />
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-text-secondary">
                        RAM
                      </p>
                      <p className="text-sm font-mono font-medium text-text-primary">
                        {model.requirements.ram}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-surface/50 border border-border/30">
                    <HardDrive size={16} className="text-accent" />
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-text-secondary">
                        Disk Space
                      </p>
                      <p className="text-sm font-mono font-medium text-text-primary">
                        {model.requirements.disk}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* HuggingFace link */}
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">
                  Source
                </h3>
                <a
                  href={model.huggingface}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary-hover transition-colors"
                >
                  <ExternalLink size={14} />
                  View on HuggingFace
                </a>
              </div>

              {/* Download progress */}
              {isDownloading && (
                <div className="p-4 rounded-xl bg-surface/50 border border-border/30">
                  <p className="text-sm font-medium text-text-primary mb-3">
                    Downloading...
                  </p>
                  <DownloadProgress
                    progress={state.progress}
                    speed={state.speed}
                    eta={state.eta}
                    onCancel={onCancel}
                  />
                </div>
              )}
            </div>

            {/* Footer actions */}
            <div className="p-6 border-t border-border/50 flex gap-3">
              {isDownloading ? (
                <Button
                  variant="danger"
                  className="flex-1"
                  onClick={onCancel}
                >
                  Cancel Download
                </Button>
              ) : isInstalled ? (
                <>
                  <Button
                    variant="secondary"
                    className="flex-1"
                    onClick={() => {
                      /* Open model folder - Tauri integration */
                    }}
                  >
                    <FolderOpen size={16} />
                    Open Folder
                  </Button>
                  <Button
                    variant="danger"
                    className="flex-1"
                    onClick={onRemove}
                  >
                    <Trash2 size={16} />
                    Remove
                  </Button>
                </>
              ) : (
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={onDownload}
                >
                  <Download size={16} />
                  Download Model
                </Button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

ModelDetails.displayName = "ModelDetails";

/* ---- Benchmark item sub-component ---- */

interface BenchmarkItemProps {
  icon: React.FC<{ size?: string | number; className?: string }>;
  label: string;
  value: string;
  unit?: string;
}

const BenchmarkItem: React.FC<BenchmarkItemProps> = ({
  icon: Icon,
  label,
  value,
  unit,
}) => (
  <div className="p-3 rounded-lg bg-surface/50 border border-border/30 space-y-2">
    <div className="flex items-center gap-1.5 text-text-secondary">
      <Icon size={14} />
      <span className="text-[10px] uppercase tracking-wider">{label}</span>
    </div>
    <p className="text-sm font-mono font-medium text-text-primary">
      {value}
      {unit && (
        <span className="text-text-secondary text-xs ml-1">{unit}</span>
      )}
    </p>
  </div>
);
