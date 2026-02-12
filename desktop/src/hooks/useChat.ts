import { useState, useCallback, useRef } from "react";
import { sendInference, getNodeStatus, isTauri } from "@/lib/tauri";
import { getMockResponse, generateTitle } from "@/lib/mockResponses";

export interface MessageMetadata {
  tokens_per_second?: number;
  energy_mj?: number;
  model?: string;
  backend?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  metadata?: MessageMetadata;
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
  energyMj: number;
  backend: string;
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
            "Welcome to **ARIA Protocol's** local inference engine! Running entirely on your device using BitNet.\n\nTry asking me about:\n- The ARIA Protocol and decentralized AI\n- BitNet model benchmarks and performance\n- Energy efficiency of 1-bit LLMs\n- Or anything else you'd like to chat about!",
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
    energyMj: 0,
    backend: "",
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

      const convId = activeConversationId;

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

      setIsGenerating(true);
      abortRef.current = false;

      // Check if backend is running (Tauri mode)
      let backendRunning = false;
      if (isTauri()) {
        try {
          const status = await getNodeStatus();
          backendRunning = status.running;
        } catch {
          backendRunning = false;
        }
      }

      if (isTauri() && !backendRunning) {
        // Backend not running — show system error, no mock fallback
        const errorMsg: Message = {
          id: createId(),
          role: "system",
          content:
            "ARIA backend is not running. Click **Start Node** on the Dashboard to begin.",
          timestamp: Date.now(),
        };

        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== convId) return c;
            return {
              ...c,
              messages: [...c.messages, errorMsg],
              updatedAt: Date.now(),
            };
          })
        );
        setIsGenerating(false);
        return;
      }

      if (isTauri() && backendRunning) {
        // ── REAL INFERENCE via Tauri backend ──
        try {
          const startTime = Date.now();
          const result = await sendInference(content, selectedModel);
          const elapsed = Date.now() - startTime;

          const assistantMsg: Message = {
            id: createId(),
            role: "assistant",
            content: result.text || "No response from backend.",
            timestamp: Date.now(),
            metadata: {
              tokens_per_second: result.tokens_per_second,
              energy_mj: result.energy_mj,
              model: result.model,
              backend: result.backend ?? "native",
            },
          };

          setGenerationStats({
            tokensGenerated: Math.ceil(
              result.tokens_per_second * (elapsed / 1000)
            ),
            tokensPerSecond: result.tokens_per_second,
            elapsedMs: elapsed,
            energyMj: result.energy_mj,
            backend: result.backend ?? "native",
          });

          setConversations((prev) =>
            prev.map((c) => {
              if (c.id !== convId) return c;
              return {
                ...c,
                messages: [...c.messages, assistantMsg],
                updatedAt: Date.now(),
              };
            })
          );

          setIsGenerating(false);
          return;
        } catch (err) {
          // Inference failed — show error, no mock fallback
          const errorMsg: Message = {
            id: createId(),
            role: "system",
            content: `Inference error: ${err}. Check that a model is loaded.`,
            timestamp: Date.now(),
          };

          setConversations((prev) =>
            prev.map((c) => {
              if (c.id !== convId) return c;
              return {
                ...c,
                messages: [...c.messages, errorMsg],
                updatedAt: Date.now(),
              };
            })
          );
          setIsGenerating(false);
          return;
        }
      }

      // FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
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
                role: "assistant" as const,
                content: "",
                timestamp: Date.now(),
                metadata: { backend: "mock" },
              },
            ],
            updatedAt: Date.now(),
          };
        })
      );

      // Typewriter effect for mock mode
      let charIndex = 0;
      const totalChars = fullResponse.length;
      const duration = 2000 + Math.random() * 2000;
      const charInterval = duration / totalChars;
      const statsStart = Date.now();

      await new Promise<void>((resolve) => {
        intervalRef.current = setInterval(() => {
          if (abortRef.current) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            resolve();
            return;
          }

          const charsToAdd = Math.max(1, Math.floor(Math.random() * 3) + 1);
          charIndex = Math.min(charIndex + charsToAdd, totalChars);
          const currentText = fullResponse.slice(0, charIndex);
          const tokenCount = Math.floor(charIndex / 4);
          const elapsedMs = Date.now() - statsStart;
          const tokPerSec =
            elapsedMs > 0 ? (tokenCount / elapsedMs) * 1000 : 0;

          setGenerationStats({
            tokensGenerated: tokenCount,
            tokensPerSecond: Math.round(tokPerSec * 10) / 10,
            elapsedMs,
            energyMj: 0,
            backend: "mock",
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
    [activeConversationId, isGenerating, selectedModel]
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
