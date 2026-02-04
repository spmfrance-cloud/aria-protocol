import React from "react";
import { cn } from "@/lib/utils";

const variants = {
  default: "bg-primary-muted text-primary border-primary/20",
  success: "bg-success-muted text-success border-success/20",
  warning: "bg-warning-muted text-warning border-warning/20",
  error: "bg-error-muted text-error border-error/20",
  outline: "bg-transparent text-text-secondary border-border",
} as const;

type BadgeVariant = keyof typeof variants;

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = "default",
  children,
  ...props
}) => {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1",
        "px-2.5 py-0.5 rounded-full",
        "text-xs font-medium",
        "border",
        "transition-colors duration-200",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

Badge.displayName = "Badge";
