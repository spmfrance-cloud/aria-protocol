# ARIA Desktop

Cross-platform desktop application for the ARIA Protocol, built with **Tauri 2.0** (primary) and **Electron** (alternative).

## Tech Stack

- **Primary Build**: Tauri 2.0 (Rust) — lightweight, fast, small binary
- **Alternative Build**: Electron — maximum compatibility
- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS + custom design system
- **Animations**: Framer Motion
- **Charts**: Recharts
- **i18n**: 12 languages supported

## Prerequisites

### For Tauri builds

- [Node.js](https://nodejs.org/) >= 18
- [Rust](https://www.rust-lang.org/tools/install) (latest stable)
- Platform-specific dependencies:

**Ubuntu / Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev \
  libappindicator3-dev \
  librsvg2-dev \
  patchelf \
  libgtk-3-dev \
  libayatana-appindicator3-dev
```

**macOS:**
```bash
xcode-select --install
```

**Windows:**
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with "Desktop development with C++"
- [WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (pre-installed on Windows 10/11)

### For Electron builds

- [Node.js](https://nodejs.org/) >= 18

## Getting Started

```bash
# Install dependencies
npm install
```

### Development (Tauri)

```bash
# Start Tauri dev server with hot-reload
npm run tauri:dev
```

### Development (Electron)

```bash
# Build the frontend first
npm run build

# Start Electron in dev mode
npm run electron:dev
```

### Development (Browser only)

```bash
# Start Vite dev server (no native features)
npm run dev
```

## Building for Production

### Tauri (Recommended)

```bash
# Build for current platform
npm run tauri:build

# Platform-specific builds
npm run tauri:build:windows     # Windows (NSIS + WiX)
npm run tauri:build:mac         # macOS Intel (DMG)
npm run tauri:build:mac-arm     # macOS Apple Silicon (DMG)
npm run tauri:build:linux       # Linux (AppImage + deb)
```

Build output: `desktop/src-tauri/target/release/bundle/`

### Electron (Alternative)

```bash
# Build for current platform
npm run electron:build

# Platform-specific builds
npm run electron:build:windows  # Windows (NSIS installer)
npm run electron:build:mac      # macOS (DMG)
npm run electron:build:linux    # Linux (AppImage + deb + rpm)
```

Build output: `desktop/release/`

## Project Structure

```
desktop/
├── src-tauri/               # Tauri/Rust backend
│   ├── Cargo.toml           # Rust dependencies & release profile
│   ├── tauri.conf.json      # Tauri config (window, bundle, plugins)
│   ├── build.rs             # Build script
│   ├── icons/               # App icons (all platforms)
│   │   ├── 32x32.png
│   │   ├── 128x128.png
│   │   ├── 128x128@2x.png
│   │   ├── icon.png         # 512x512 (Linux)
│   │   ├── icon.ico         # Windows
│   │   └── icon.icns        # macOS
│   └── src/
│       ├── main.rs          # Tauri entry point
│       └── lib.rs           # ARIA commands & state
│
├── electron/                # Electron alternative
│   ├── main.js              # Main process
│   ├── preload.js           # Secure bridge (contextBridge)
│   └── package.json         # Electron metadata
│
├── src/                     # React frontend (shared)
│   ├── main.tsx             # Entry point
│   ├── App.tsx              # Router & layout
│   ├── components/          # UI components (31 files)
│   ├── pages/               # Page views (6 pages)
│   ├── hooks/               # React hooks (4 hooks)
│   ├── i18n/                # Translations (12 languages)
│   ├── lib/
│   │   ├── utils.ts         # Utility helpers
│   │   ├── mockResponses.ts # Mock data for demo
│   │   ├── tauri.ts         # Tauri command wrapper
│   │   └── api.ts           # Unified API (Tauri/Electron/Web)
│   └── styles/
│       └── theme.ts         # Design tokens
│
├── electron-builder.json    # Electron Builder config
├── package.json             # Dependencies & scripts
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind CSS config
├── vite.config.ts           # Vite bundler config
└── index.html               # HTML entry
```

## Architecture

The frontend communicates with the ARIA backend through a unified API layer:

```
┌─────────────────────────────────────────────────┐
│                 React Frontend                   │
│             (src/lib/api.ts)                     │
├────────────┬────────────────┬───────────────────┤
│   Tauri    │    Electron    │     Web (Dev)     │
│  invoke()  │     IPC        │   Mock data       │
├────────────┼────────────────┼───────────────────┤
│ Rust → Python │ Node.js → Python │              │
│   (sidecar)   │   (subprocess)   │              │
└───────────────┴──────────────────┴──────────────┘
                       ↕
              ARIA Protocol Backend
              (Python, port 3000)
```

- **Tauri**: Uses `invoke()` to call Rust commands, which communicate with the ARIA Python backend via HTTP
- **Electron**: Uses IPC to call Node.js handlers, which communicate with the ARIA Python backend via HTTP
- **Web**: Falls back to mock data for development without a backend

## Tauri vs Electron

| Feature | Tauri | Electron |
|---------|-------|----------|
| Binary size | ~10 MB | ~150 MB |
| Memory usage | ~30 MB | ~150 MB |
| Startup time | Fast | Moderate |
| Web engine | System WebView | Bundled Chromium |
| Backend | Rust | Node.js |
| Auto-update | Built-in plugin | electron-updater |
| Compatibility | Requires WebView2/WebKitGTK | Works everywhere |

**Recommendation**: Use Tauri for production releases. Use Electron as a fallback for environments where system WebView is unavailable.

## Troubleshooting

### Tauri build fails on Ubuntu

Install all required system dependencies:
```bash
sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev \
  librsvg2-dev patchelf libgtk-3-dev libayatana-appindicator3-dev
```

### Rust compilation errors

Ensure you have the latest stable Rust:
```bash
rustup update stable
```

### Electron build fails on macOS

Disable code signing for local builds:
```bash
CSC_IDENTITY_AUTO_DISCOVERY=false npm run electron:build:mac
```

### Frontend hot-reload not working in Tauri

Check that Vite is running on port 5173 and `devUrl` in `tauri.conf.json` matches.

### ARIA backend not connecting

Ensure the ARIA Python backend is running:
```bash
pip install aria-protocol
aria node start --port 8765 --api-port 3000
```

## Supported Platforms

| Platform | Architecture | Tauri | Electron |
|----------|-------------|-------|----------|
| Windows 10+ | x64 | NSIS, WiX | NSIS |
| macOS 11+ | x64, ARM64 | DMG, app bundle | DMG |
| Ubuntu 20.04+ | x64 | AppImage, deb | AppImage, deb, rpm |

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
