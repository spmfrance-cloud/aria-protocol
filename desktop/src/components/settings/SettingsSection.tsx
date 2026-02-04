import React from "react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface SettingsSectionProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
}

export const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  description,
  icon: Icon,
  children,
}) => {
  return (
    <div
      className={cn(
        "rounded-xl",
        "bg-surface/60 backdrop-blur-md",
        "border border-border/50",
        "overflow-hidden"
      )}
    >
      <div className="px-6 py-4 border-b border-border/40">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Icon size={16} className="text-primary" />
            </div>
          )}
          <div>
            <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
            {description && (
              <p className="text-xs text-text-secondary mt-0.5">
                {description}
              </p>
            )}
          </div>
        </div>
      </div>
      <div className="divide-y divide-border/30">{children}</div>
    </div>
  );
};
