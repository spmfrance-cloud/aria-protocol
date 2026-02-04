import React from "react";
import { cn } from "@/lib/utils";

interface SliderInputProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  unit?: string;
  disabled?: boolean;
}

export const SliderInput: React.FC<SliderInputProps> = ({
  value,
  min,
  max,
  step = 1,
  onChange,
  unit = "",
  disabled = false,
}) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="flex items-center gap-3 min-w-[200px]">
      <div className="flex-1 relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(Number(e.target.value))}
          className={cn(
            "w-full h-1.5 rounded-full appearance-none cursor-pointer",
            "bg-border/60",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "[&::-webkit-slider-thumb]:appearance-none",
            "[&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4",
            "[&::-webkit-slider-thumb]:rounded-full",
            "[&::-webkit-slider-thumb]:bg-primary",
            "[&::-webkit-slider-thumb]:shadow-[0_0_8px_rgba(99,102,241,0.5)]",
            "[&::-webkit-slider-thumb]:cursor-pointer",
            "[&::-webkit-slider-thumb]:transition-shadow [&::-webkit-slider-thumb]:duration-200",
            "[&::-webkit-slider-thumb]:hover:shadow-[0_0_12px_rgba(99,102,241,0.7)]",
            "[&::-moz-range-thumb]:border-none",
            "[&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4",
            "[&::-moz-range-thumb]:rounded-full",
            "[&::-moz-range-thumb]:bg-primary",
            "[&::-moz-range-thumb]:cursor-pointer"
          )}
          style={{
            background: `linear-gradient(to right, rgb(99 102 241) 0%, rgb(34 211 238) ${percentage}%, rgb(30 30 46 / 0.6) ${percentage}%)`,
          }}
        />
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-text-secondary/50">
            {min}
            {unit}
          </span>
          <span className="text-[10px] text-text-secondary/50">
            {max}
            {unit}
          </span>
        </div>
      </div>
      <div className="w-16 text-right">
        <span className="text-sm font-mono font-medium text-text-primary">
          {value}
          {unit}
        </span>
      </div>
    </div>
  );
};
