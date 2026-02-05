import { useRef, useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { MessageSquare, Menu, X, Wifi } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ConversationList } from "@/components/chat/ConversationList";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { ChatStats } from "@/components/chat/ChatStats";
import { useChat } from "@/hooks/useChat";
import { useBackend } from "@/hooks/useBackend";
import { cn } from "@/lib/utils";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

export default function Chat() {
  const { t } = useTranslation();
  const {
    conversations,
    activeConversationId,
    messages,
    isGenerating,
    generationStats,
    selectedModel,
    setSelectedModel,
    sendMessage,
    createConversation,
    deleteConversation,
    switchConversation,
    stopGeneration,
  } = useChat();
  const { available } = useBackend();

  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Wrap sendMessage to pass backend availability
  const handleSendMessage = useCallback(
    (content: string) => {
      sendMessage(content, available);
    },
    [sendMessage, available]
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isGenerating]);

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="h-[calc(100vh-2rem)] flex flex-col max-w-[1400px]"
    >
      {/* Page header */}
      <motion.header
        variants={item}
        className="flex items-center justify-between mb-4"
      >
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-text-primary">
            AI Assistant
          </h1>
          <Badge variant="success">
            <Wifi size={12} />
            Local
          </Badge>
          {/* Connection status badge */}
          <Badge
            variant={available ? "success" : "outline"}
            className={cn(
              "text-xs gap-1 px-2 py-0.5",
              available
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "bg-zinc-700/50 text-zinc-400 border-zinc-600/30"
            )}
          >
            <div className={cn(
              "w-1.5 h-1.5 rounded-full",
              available ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"
            )} />
            {available ? t("chat.liveMode") : t("chat.mockMode")}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <ChatStats
            stats={generationStats}
            isGenerating={isGenerating}
          />
        </div>
      </motion.header>

      {/* Main chat area */}
      <motion.div
        variants={item}
        className={cn(
          "flex-1 flex overflow-hidden",
          "rounded-xl border border-border/50",
          "bg-background/50"
        )}
      >
        {/* Sidebar — desktop */}
        <div className="hidden lg:block w-[280px] flex-shrink-0">
          <ConversationList
            conversations={conversations}
            activeId={activeConversationId}
            onSelect={switchConversation}
            onCreate={createConversation}
            onDelete={deleteConversation}
          />
        </div>

        {/* Mobile sidebar overlay */}
        <AnimatePresence>
          {sidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="fixed inset-0 bg-background/60 backdrop-blur-sm z-50 lg:hidden"
                onClick={() => setSidebarOpen(false)}
              />
              <motion.div
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: "spring", stiffness: 400, damping: 35 }}
                className="fixed left-0 top-0 bottom-0 w-[280px] z-50 lg:hidden"
              >
                <ConversationList
                  conversations={conversations}
                  activeId={activeConversationId}
                  onSelect={switchConversation}
                  onCreate={createConversation}
                  onDelete={deleteConversation}
                  onClose={() => setSidebarOpen(false)}
                  className="h-full"
                />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Chat column */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat header bar */}
          <div
            className={cn(
              "flex items-center gap-3 px-4 h-12",
              "border-b border-border/40",
              "bg-surface/40 backdrop-blur-sm"
            )}
          >
            {/* Mobile hamburger */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-text-secondary hover:text-text-primary transition-colors"
            >
              {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
            </button>

            <div className="flex items-center gap-2 min-w-0">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-[10px]">A</span>
              </div>
              <span className="text-sm font-medium text-text-primary truncate">
                {selectedModel}
              </span>
              <Badge variant="success" className="text-[10px] py-0 px-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                {t("dashboard.online")}
              </Badge>
            </div>
          </div>

          {/* Messages area */}
          <div
            ref={scrollContainerRef}
            className="flex-1 overflow-y-auto scroll-smooth"
          >
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 25 }}
                >
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 border border-primary/20 flex items-center justify-center mb-4 mx-auto">
                    <MessageSquare size={28} className="text-primary" />
                  </div>
                  <h2 className="text-lg font-semibold text-text-primary mb-1">
                    Start a conversation
                  </h2>
                  <p className="text-sm text-text-secondary/60 max-w-sm">
                    Ask about ARIA Protocol, BitNet models, decentralized AI,
                    or anything you'd like to discuss.
                  </p>
                </motion.div>
              </div>
            ) : (
              <div className="py-4 space-y-1">
                {messages.map((msg, i) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    isStreaming={
                      isGenerating &&
                      msg.role === "assistant" &&
                      i === messages.length - 1
                    }
                  />
                ))}

                {/* Typing indicator — shows briefly before first character appears */}
                <AnimatePresence>
                  {isGenerating &&
                    messages[messages.length - 1]?.role === "user" && (
                      <TypingIndicator />
                    )}
                </AnimatePresence>

                <div ref={messagesEndRef} className="h-1" />
              </div>
            )}
          </div>

          {/* Input */}
          <ChatInput
            onSend={handleSendMessage}
            onStop={stopGeneration}
            isGenerating={isGenerating}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
          />
        </div>
      </motion.div>
    </motion.div>
  );
}
