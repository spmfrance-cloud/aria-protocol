import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { Conversation } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
  collapsed?: boolean;
  onClose?: () => void;
  className?: string;
}

const listContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const listItem = {
  hidden: { opacity: 0, x: -12 },
  show: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: "easeOut" },
  },
};

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  activeId,
  onSelect,
  onCreate,
  onDelete,
  collapsed: _collapsed = false,
  onClose,
  className,
}) => {
  const handleSelect = (id: string) => {
    onSelect(id);
    onClose?.();
  };

  return (
    <div
      className={cn(
        "flex flex-col h-full",
        "bg-surface/60 backdrop-blur-xl",
        "border-r border-border/50",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-border/40">
        <h2 className="text-sm font-semibold text-text-primary">
          Conversations
        </h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onCreate}
          className={cn(
            "w-8 h-8 rounded-lg",
            "bg-primary/15 text-primary",
            "flex items-center justify-center",
            "hover:bg-primary/25 transition-colors duration-150"
          )}
        >
          <Plus size={16} />
        </motion.button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto py-2 px-2">
        <motion.div
          variants={listContainer}
          initial="hidden"
          animate="show"
          className="space-y-0.5"
        >
          <AnimatePresence mode="popLayout">
            {conversations.map((conv) => {
              const isActive = conv.id === activeId;
              const lastMessage = conv.messages[conv.messages.length - 1];
              const preview = lastMessage
                ? lastMessage.content.slice(0, 60).replace(/[#*`]/g, "") +
                  (lastMessage.content.length > 60 ? "..." : "")
                : "No messages yet";

              return (
                <motion.div
                  key={conv.id}
                  variants={listItem}
                  layout
                  exit={{ opacity: 0, x: -20, transition: { duration: 0.2 } }}
                >
                  <div
                    role="button"
                    tabIndex={0}
                    onClick={() => handleSelect(conv.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") handleSelect(conv.id);
                    }}
                    className={cn(
                      "group w-full text-left rounded-lg cursor-pointer",
                      "px-3 py-2.5",
                      "transition-all duration-150",
                      isActive
                        ? "bg-primary/10 border border-primary/20"
                        : "border border-transparent hover:bg-background/50 hover:border-border/30"
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <MessageSquare
                          size={14}
                          className={cn(
                            "flex-shrink-0 mt-0.5",
                            isActive
                              ? "text-primary"
                              : "text-text-secondary/50"
                          )}
                        />
                        <div className="min-w-0">
                          <p
                            className={cn(
                              "text-sm font-medium truncate",
                              isActive
                                ? "text-text-primary"
                                : "text-text-secondary group-hover:text-text-primary"
                            )}
                          >
                            {conv.title}
                          </p>
                          <p className="text-[11px] text-text-secondary/40 truncate mt-0.5">
                            {preview}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-1 flex-shrink-0">
                        <span className="text-[10px] text-text-secondary/30 whitespace-nowrap group-hover:hidden">
                          {formatDistanceToNow(conv.updatedAt, {
                            addSuffix: false,
                          })}
                        </span>

                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(conv.id);
                          }}
                          className={cn(
                            "hidden group-hover:flex",
                            "w-6 h-6 rounded-md",
                            "items-center justify-center",
                            "text-text-secondary/40 hover:text-error",
                            "hover:bg-error/10",
                            "transition-colors duration-150"
                          )}
                        >
                          <Trash2 size={12} />
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border/40">
        <p className="text-[10px] text-text-secondary/30 text-center">
          {conversations.length} conversation
          {conversations.length !== 1 ? "s" : ""}
        </p>
      </div>
    </div>
  );
};

ConversationList.displayName = "ConversationList";
