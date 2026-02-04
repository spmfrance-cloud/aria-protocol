import { useState, useCallback, useRef } from "react";
import { getMockResponse, generateTitle } from "@/lib/mockResponses";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

export interface GenerationStats {
  tokensGenerated: number;
  tokensPerSecond: number;
  elapsedMs: number;
}

function createId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const welcome: Conversation = {
      id: "welcome",
      title: "Welcome to ARIA",
      messages: [
        {
          id: "welcome-msg",
          role: "assistant",
          content:
            "Welcome to **ARIA Protocol's** local AI assistant! I'm running entirely on your device using BitNet inference.\n\nTry asking me about:\n- The ARIA Protocol and decentralized AI\n- BitNet model benchmarks and performance\n- Energy efficiency of 1-bit LLMs\n- Or anything else you'd like to chat about!",
          timestamp: Date.now() - 60000,
        },
      ],
      createdAt: Date.now() - 60000,
      updatedAt: Date.now() - 60000,
    };
    return [welcome];
  });

  const [activeConversationId, setActiveConversationId] = useState("welcome");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStats, setGenerationStats] = useState<GenerationStats>({
    tokensGenerated: 0,
    tokensPerSecond: 0,
    elapsedMs: 0,
  });
  const [selectedModel, setSelectedModel] = useState("BitNet-b1.58-2B-4T");

  const abortRef = useRef(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId
  );
  const messages = activeConversation?.messages ?? [];

  const createConversation = useCallback(() => {
    const id = createId();
    const conv: Conversation = {
      id,
      title: "New conversation",
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setConversations((prev) => [conv, ...prev]);
    setActiveConversationId(id);
    return id;
  }, []);

  const deleteConversation = useCallback(
    (id: string) => {
      setConversations((prev) => {
        const next = prev.filter((c) => c.id !== id);
        if (next.length === 0) {
          const fallback: Conversation = {
            id: createId(),
            title: "New conversation",
            messages: [],
            createdAt: Date.now(),
            updatedAt: Date.now(),
          };
          next.push(fallback);
        }
        if (id === activeConversationId) {
          setActiveConversationId(next[0].id);
        }
        return next;
      });
    },
    [activeConversationId]
  );

  const switchConversation = useCallback((id: string) => {
    setActiveConversationId(id);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (isGenerating) return;

      let convId = activeConversationId;

      // If current conversation has no messages, use it; otherwise check if we need it
      const userMsg: Message = {
        id: createId(),
        role: "user",
        content,
        timestamp: Date.now(),
      };

      // Update conversation with user message
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== convId) return c;
          const isFirst = c.messages.length === 0;
          return {
            ...c,
            title: isFirst ? generateTitle(content) : c.title,
            messages: [...c.messages, userMsg],
            updatedAt: Date.now(),
          };
        })
      );

      // Start generation
      setIsGenerating(true);
      abortRef.current = false;

      const fullResponse = getMockResponse(content);
      const assistantMsgId = createId();

      // Add empty assistant message
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== convId) return c;
          return {
            ...c,
            messages: [
              ...c.messages,
              {
                id: assistantMsgId,
                role: "assistant",
                content: "",
                timestamp: Date.now(),
              },
            ],
            updatedAt: Date.now(),
          };
        })
      );

      // Typewriter effect — character by character
      let charIndex = 0;
      const totalChars = fullResponse.length;
      // Calculate interval to finish in 2-4 seconds
      const duration = 2000 + Math.random() * 2000;
      const charInterval = duration / totalChars;

      const statsStart = Date.now();
      let tokenCount = 0;

      await new Promise<void>((resolve) => {
        intervalRef.current = setInterval(() => {
          if (abortRef.current) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            resolve();
            return;
          }

          // Add a few characters at a time for smoother rendering
          const charsToAdd = Math.max(1, Math.floor(Math.random() * 3) + 1);
          charIndex = Math.min(charIndex + charsToAdd, totalChars);

          const currentText = fullResponse.slice(0, charIndex);

          // Approximate tokens (roughly 1 token per 4 chars)
          tokenCount = Math.floor(charIndex / 4);
          const elapsedMs = Date.now() - statsStart;
          const tokPerSec =
            elapsedMs > 0 ? (tokenCount / elapsedMs) * 1000 : 0;

          setGenerationStats({
            tokensGenerated: tokenCount,
            tokensPerSecond: Math.round(tokPerSec * 10) / 10,
            elapsedMs,
          });

          setConversations((prev) =>
            prev.map((c) => {
              if (c.id !== convId) return c;
              return {
                ...c,
                messages: c.messages.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: currentText }
                    : m
                ),
                updatedAt: Date.now(),
              };
            })
          );

          if (charIndex >= totalChars) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            resolve();
          }
        }, charInterval);
      });

      setIsGenerating(false);
    },
    [activeConversationId, isGenerating]
  );

  const stopGeneration = useCallback(() => {
    abortRef.current = true;
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsGenerating(false);
  }, []);

  return {
    conversations,
    activeConversationId,
    activeConversation,
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
  };
}
