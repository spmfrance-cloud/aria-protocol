/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
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
        "text-primary": "#f8fafc",
        "text-secondary": "#94a3b8",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "progress-fill": "progress-fill 1s ease-out forwards",
      },
      keyframes: {
        "glow-pulse": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "0.8" },
        },
        "progress-fill": {
          "0%": { width: "0%" },
          "100%": { width: "var(--progress-width)" },
        },
      },
    },
  },
  plugins: [],
};
