import React from "react";
import { motion } from "framer-motion";
import {
  Download,
  Trash2,
  Cpu,
  Gauge,
  HardDrive,
  Star,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DownloadProgress } from "./DownloadProgress";
import type { ModelInfo, ModelState } from "@/hooks/useModels";

interface ModelCardProps {
  model: ModelInfo;
  state: ModelState;
  onDownload: () => void;
  onCancel: () => void;
  onRemove: () => void;
  onClick: () => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({
  model,
  state,
  onDownload,
  onCancel,
  onRemove,
  onClick,
}) => {
  const isDownloading = state.status === "downloading";
  const isInstalled = state.status === "installed";

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={cn(
        "relative rounded-xl cursor-pointer",
        "bg-surface/80 backdrop-blur-md",
        "border border-border/50",
        "transition-all duration-200",
        "hover:border-primary/30 hover:shadow-[0_0_30px_rgba(99,102,241,0.12)]",
        isInstalled &&
          "border-success/20 hover:border-success/40 hover:shadow-[0_0_30px_rgba(16,185,129,0.12)]"
      )}
    >
      {/* Recommended badge */}
      {model.recommended && (
        <div className="absolute -top-2.5 right-4 z-10">
          <Badge
            variant="warning"
            className="shadow-lg shadow-warning/20"
          >
            <Star size={10} className="fill-current" />
            Recommended
          </Badge>
        </div>
      )}

      <div className="p-5">
        {/* Model icon + header */}
        <div className="flex items-start gap-4 mb-4">
          <div
            className={cn(
              "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0",
              isInstalled
                ? "bg-success-muted"
                : "bg-gradient-to-br from-primary/20 to-accent/20"
            )}
          >
            {isInstalled ? (
              <CheckCircle2 size={24} className="text-success" />
            ) : (
              <Cpu size={24} className="text-primary" />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-semibold text-text-primary truncate">
              {model.name}
            </h3>
            <p className="text-xs text-text-secondary mt-0.5">
              {model.params} parameters
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-text-secondary">
              <Gauge size={12} />
              <span className="text-[10px] uppercase tracking-wider">
                Speed
              </span>
            </div>
            <p className="text-xs font-mono font-medium text-text-primary">
              {model.performance}
            </p>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-text-secondary">
              <HardDrive size={12} />
              <span className="text-[10px] uppercase tracking-wider">
                Size
              </span>
            </div>
            <p className="text-xs font-mono font-medium text-text-primary">
              {model.size}
            </p>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-text-secondary">
              <Cpu size={12} />
              <span className="text-[10px] uppercase tracking-wider">
                RAM
              </span>
            </div>
            <p className="text-xs font-mono font-medium text-text-primary">
              {model.ram}
            </p>
          </div>
        </div>

        {/* Download progress or action button */}
        {isDownloading ? (
          <DownloadProgress
            progress={state.progress}
            speed={state.speed}
            eta={state.eta}
            onCancel={onCancel}
          />
        ) : (
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex gap-2"
          >
            {isInstalled ? (
              <Button
                variant="danger"
                size="sm"
                className="w-full"
                onClick={onRemove}
              >
                <Trash2 size={14} />
                Remove
              </Button>
            ) : (
              <Button
                variant="primary"
                size="sm"
                className="w-full"
                onClick={onDownload}
              >
                <Download size={14} />
                Download
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Installed indicator line */}
      {isInstalled && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-success/0 via-success to-success/0 rounded-b-xl"
        />
      )}
    </motion.div>
  );
};

ModelCard.displayName = "ModelCard";
