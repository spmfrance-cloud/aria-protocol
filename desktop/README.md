# ARIA Desktop

Cross-platform desktop application for the ARIA Protocol, built with Tauri 2.0 and React.

## Tech Stack

- **Backend**: Tauri 2.0 (Rust)
- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS + custom design system
- **Animations**: Framer Motion
- **Components**: Custom UI library (shadcn/ui inspired)

## Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- [Rust](https://www.rust-lang.org/tools/install) (latest stable)
- [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/)

## Getting Started

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev

# Build for production
npm run tauri build
```

## Project Structure

```
desktop/
├── src-tauri/           # Tauri/Rust backend
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── src/
│       └── main.rs
├── src/                 # React frontend
│   ├── main.tsx         # Entry point
│   ├── App.tsx          # Demo / main app
│   ├── index.css        # Tailwind + custom styles
│   ├── components/
│   │   └── ui/          # Design system components
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Input.tsx
│   │       ├── Badge.tsx
│   │       ├── Progress.tsx
│   │       └── index.ts
│   ├── lib/
│   │   └── utils.ts     # Utility helpers
│   └── styles/
│       └── theme.ts     # Design tokens
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## Design System

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#0a0a0f` | App background |
| Surface | `#12121a` | Cards, panels |
| Border | `#1e1e2e` | Subtle borders |
| Primary | `#6366f1` | Actions, links |
| Accent | `#22d3ee` | Highlights, stats |
| Success | `#10b981` | Positive states |
| Warning | `#f59e0b` | Caution states |
| Error | `#ef4444` | Error states |

### Components

- **Button** — `primary`, `secondary`, `ghost`, `danger` variants with `sm`, `md`, `lg` sizes and loading state
- **Card** — Glassmorphism with optional glow border, header/content/footer slots
- **Input** — Label, error state, icon support (left/right positioning)
- **Badge** — `default`, `success`, `warning`, `error`, `outline` variants
- **Progress** — Animated linear progress bar with multiple colors and sizes

### Effects

- Glassmorphism (backdrop-blur) on cards and surfaces
- Gradient border on hover (CSS mask technique)
- Glow effects on interactive elements
- Smooth 200ms transitions throughout
- Framer Motion for mount/interaction animations

## License

MIT — ARIA Protocol Contributors
