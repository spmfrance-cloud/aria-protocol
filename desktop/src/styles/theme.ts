export const theme = {
  colors: {
    background: "#0a0a0f",
    surface: "#12121a",
    border: "#1e1e2e",
    primary: {
      DEFAULT: "#6366f1",
      hover: "#818cf8",
      muted: "rgba(99, 102, 241, 0.15)",
    },
    accent: {
      DEFAULT: "#22d3ee",
      hover: "#67e8f9",
      muted: "rgba(34, 211, 238, 0.15)",
    },
    success: {
      DEFAULT: "#10b981",
      muted: "rgba(16, 185, 129, 0.15)",
    },
    warning: {
      DEFAULT: "#f59e0b",
      muted: "rgba(245, 158, 11, 0.15)",
    },
    error: {
      DEFAULT: "#ef4444",
      muted: "rgba(239, 68, 68, 0.15)",
    },
    text: {
      primary: "#f8fafc",
      secondary: "#94a3b8",
    },
  },
  fonts: {
    sans: "'Inter', system-ui, sans-serif",
    mono: "'JetBrains Mono', monospace",
  },
  transitions: {
    fast: "150ms ease",
    default: "200ms ease",
    slow: "300ms ease",
  },
  effects: {
    glowPrimary: "0 0 20px rgba(99, 102, 241, 0.3)",
    glowAccent: "0 0 20px rgba(34, 211, 238, 0.3)",
    glowSuccess: "0 0 20px rgba(16, 185, 129, 0.3)",
    glowError: "0 0 20px rgba(239, 68, 68, 0.3)",
    glassBg: "rgba(18, 18, 26, 0.8)",
    glassBorder: "rgba(30, 30, 46, 0.5)",
  },
} as const;

export type Theme = typeof theme;
