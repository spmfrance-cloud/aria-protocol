import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
  icon?: string;
}

interface SelectDropdownProps {
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const SelectDropdown: React.FC<SelectDropdownProps> = ({
  value,
  options,
  onChange,
  disabled = false,
}) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selected = options.find((o) => o.value === value);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        disabled={disabled}
        onClick={() => setOpen(!open)}
        className={cn(
          "inline-flex items-center gap-2 h-9 px-3 rounded-lg",
          "bg-surface/80 backdrop-blur-sm",
          "border border-border/50",
          "text-sm text-text-primary",
          "transition-all duration-200",
          "hover:border-primary/40",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50",
          disabled && "opacity-50 cursor-not-allowed",
          open && "border-primary/50"
        )}
      >
        {selected?.icon && <span className="text-base">{selected.icon}</span>}
        <span className="truncate max-w-[140px]">
          {selected?.label || value}
        </span>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown size={14} className="text-text-secondary" />
        </motion.span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.97 }}
            transition={{ duration: 0.15 }}
            className={cn(
              "absolute z-50 mt-1 right-0 min-w-[180px]",
              "rounded-lg overflow-hidden",
              "bg-surface/95 backdrop-blur-xl",
              "border border-border/50",
              "shadow-xl shadow-black/30",
              "max-h-[280px] overflow-y-auto"
            )}
          >
            {options.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  onChange(option.value);
                  setOpen(false);
                }}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2 text-sm",
                  "transition-colors duration-150",
                  option.value === value
                    ? "bg-primary/15 text-primary"
                    : "text-text-primary hover:bg-surface"
                )}
              >
                {option.icon && (
                  <span className="text-base">{option.icon}</span>
                )}
                <span className="truncate">{option.label}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
