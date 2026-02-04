import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Square, ChevronDown, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";

const AVAILABLE_MODELS = [
  { id: "bitnet-2b-4t", label: "BitNet-b1.58-2B-4T", badge: "Recommended" },
  { id: "bitnet-large", label: "BitNet-b1.58-large", badge: "Fast" },
  { id: "llama3-8b", label: "Llama3-8B-1.58", badge: "8B" },
];

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isGenerating: boolean;
  selectedModel: string;
  onModelChange: (model: string) => void;
  className?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  isGenerating,
  selectedModel,
  onModelChange,
  className,
}) => {
  const [value, setValue] = useState("");
  const [showModelPicker, setShowModelPicker] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const pickerRef = useRef<HTMLDivElement>(null);

  const canSend = value.trim().length > 0 && !isGenerating;

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const maxHeight = 5 * 24; // 5 lines * ~24px line-height
    el.style.height = Math.min(el.scrollHeight, maxHeight) + "px";
  }, [value]);

  // Close model picker on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        pickerRef.current &&
        !pickerRef.current.contains(e.target as Node)
      ) {
        setShowModelPicker(false);
      }
    };
    if (showModelPicker) {
      document.addEventListener("mousedown", handleClick);
      return () => document.removeEventListener("mousedown", handleClick);
    }
  }, [showModelPicker]);

  const handleSend = useCallback(() => {
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [canSend, value, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={cn("relative", className)}>
      {/* Shadow overlay at top */}
      <div className="absolute -top-8 left-0 right-0 h-8 bg-gradient-to-t from-background to-transparent pointer-events-none" />

      <div className="px-4 pb-4 pt-2">
        <div
          className={cn(
            "relative rounded-2xl",
            "bg-surface/90 backdrop-blur-md",
            "border border-border/60",
            "shadow-lg shadow-background/50",
            "transition-colors duration-200",
            "focus-within:border-primary/40"
          )}
        >
          {/* Model selector bar */}
          <div className="flex items-center justify-between px-4 pt-2.5 pb-1">
            <div className="relative" ref={pickerRef}>
              <button
                onClick={() => setShowModelPicker(!showModelPicker)}
                className={cn(
                  "flex items-center gap-1.5 text-xs text-text-secondary",
                  "hover:text-text-primary transition-colors duration-150",
                  "rounded-md px-2 py-1 -ml-2",
                  "hover:bg-background/50"
                )}
              >
                <Cpu size={12} />
                <span className="font-mono">{selectedModel}</span>
                <ChevronDown
                  size={10}
                  className={cn(
                    "transition-transform duration-200",
                    showModelPicker && "rotate-180"
                  )}
                />
              </button>

              {/* Model dropdown */}
              <AnimatePresence>
                {showModelPicker && (
                  <motion.div
                    initial={{ opacity: 0, y: 4, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 4, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className={cn(
                      "absolute bottom-full left-0 mb-2",
                      "w-64 rounded-xl overflow-hidden",
                      "bg-surface border border-border/60",
                      "shadow-xl shadow-background/80",
                      "backdrop-blur-xl"
                    )}
                  >
                    <div className="p-1.5">
                      {AVAILABLE_MODELS.map((model) => (
                        <button
                          key={model.id}
                          onClick={() => {
                            onModelChange(model.label);
                            setShowModelPicker(false);
                          }}
                          className={cn(
                            "w-full flex items-center justify-between gap-2",
                            "px-3 py-2 rounded-lg text-left",
                            "transition-colors duration-150",
                            selectedModel === model.label
                              ? "bg-primary/15 text-text-primary"
                              : "text-text-secondary hover:text-text-primary hover:bg-background/50"
                          )}
                        >
                          <span className="text-sm font-mono">
                            {model.label}
                          </span>
                          {model.badge && (
                            <span
                              className={cn(
                                "text-[10px] px-1.5 py-0.5 rounded-full",
                                model.badge === "Recommended"
                                  ? "bg-primary/15 text-primary"
                                  : "bg-background/60 text-text-secondary"
                              )}
                            >
                              {model.badge}
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Textarea + Send */}
          <div className="flex items-end gap-2 px-4 pb-3">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message ARIA..."
              rows={1}
              className={cn(
                "flex-1 resize-none",
                "bg-transparent text-sm text-text-primary",
                "placeholder:text-text-secondary/40",
                "outline-none",
                "leading-6 py-0.5",
                "max-h-[120px]"
              )}
            />

            {isGenerating ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onStop}
                className={cn(
                  "flex-shrink-0 w-8 h-8 rounded-lg",
                  "bg-error/20 text-error",
                  "flex items-center justify-center",
                  "hover:bg-error/30 transition-colors duration-150"
                )}
              >
                <Square size={14} />
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: canSend ? 1.05 : 1 }}
                whileTap={{ scale: canSend ? 0.95 : 1 }}
                onClick={handleSend}
                disabled={!canSend}
                className={cn(
                  "flex-shrink-0 w-8 h-8 rounded-lg",
                  "flex items-center justify-center",
                  "transition-all duration-150",
                  canSend
                    ? "bg-primary text-white hover:bg-primary-hover"
                    : "bg-border/30 text-text-secondary/30 cursor-not-allowed"
                )}
              >
                <Send size={14} />
              </motion.button>
            )}
          </div>
        </div>

        {/* Footer hint */}
        <p className="text-[10px] text-text-secondary/30 text-center mt-2">
          Running locally · No data leaves your device · Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

ChatInput.displayName = "ChatInput";
