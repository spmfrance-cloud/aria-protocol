# ARIA Protocol — Roadmap v2.1

> From v0.5.2 (current) to v1.1.0+ · 9 versions · 62 tasks
> Covers: code, docs, whitepaper, website, communication

## Changelog v2 → v2.1

Summary of 7 corrections applied to the roadmap v2.

### Critical
- **v0.5.5 #8** — Added "Finalize desktop↔backend integration". Desktop app still uses mock responses. Absolute prerequisite before testnet.
- **v0.6.0 #10** — Added "P2P network robustness". NAT traversal, reconnection, production-grade DHT. Without this, 50 nodes can't find each other.

### Important
- **v0.5.5 #9** — Added "Validate Falcon3/Edge model catalog". Verify actual GGUF availability before planning v0.6.0.
- **v0.7.0 → v0.7.0 + v0.7.5** — Split into 2 versions. v0.7.0 = network (Reputation + Router). v0.7.5 = R&D + Docs (PT-BitNet, WP v2, Site v2).
- **v0.9.0 #1** — ARIA-LM requalified: LoRA fine-tune of existing model (not training from scratch). Full training → v1.1.0+.

### Minor
- **v0.5.5 #1** — Version confirmed at v0.5.2. README badge, pyproject.toml, and GitHub release to sync.
- **v1.0.0 #7** — "Computer Use (Level 2+3)" moved to v1.1.0+. Mainnet must be 100% focused on token/DAO/audit.

---

## Overview

| Version | Name | Focus | Tasks | Status |
|---------|------|-------|-------|--------|
| v0.1→v0.5.2 | Genesis → Desktop | Whitepaper, P2P, CLI, API, Dashboard, BitNet, Benchmarks, Desktop | — | ✅ Complete |
| v0.5.5 | Housekeeping & Foundations | Repo update, backend integration, model validation, website, docs | 9 | 🔥 Next |
| v0.6.0 | Testnet Alpha | Bootstrap nodes, expanded catalog, hardened P2P, 50+ community nodes | 10 | ⬜ Planned |
| v0.7.0 | Smart Layer | Reputation, Smart Router, frontier API overlay, intelligent chat | 6 | ⬜ Planned |
| v0.7.5 | R&D + Documentation | PT-BitNet prototype, Accessibility Tree, Whitepaper v2, site v2 | 4 | ⬜ Planned |
| v0.8.0 | Collective Intelligence | Consensus Inference, RAG, ARIA Code, vision pipeline | 8 | ⬜ Planned |
| v0.9.0 | ARIA-LM v0 + Ecosystem | Community LoRA fine-tune, MCP client, browser agent, mobile R&D | 8 | ⬜ Planned |
| v1.0.0 | Mainnet | $ARIA token, DAO, staking, audit, launch | 9 | ⬜ Planned |
| v1.1.0+ | Beyond | Mobile, Computer Use, MoE+1-bit, full ARIA-LM training, SDK | 7 | 🔮 Vision |

---

## v0.1 → v0.5.2 — Genesis → Desktop ✅

All foundational milestones complete:

- **v0.1.0 — Genesis**: Whitepaper published, reference implementation
- **v0.2.0 — Full Stack**: P2P WebSocket + TLS networking, CLI, API server, real-time Dashboard, BitNet inference engine
- **v0.2.5 — Hardening**: Threat model, protocol specification, TLS support
- **v0.3.0 — Benchmarks**: Real-world performance validation with bitnet.cpp (89.65 t/s on 0.7B)
- **v0.4.0 — Native BitNet**: Direct Python ctypes bindings to bitnet.cpp
- **v0.5.0 — Desktop App**: Tauri 2.0 + Electron GUI, 12-language support, system tray, model manager
- **v0.5.2 — Subprocess Backend**: Multi-backend inference (native/subprocess/simulation), comparative benchmarks (120.25 t/s on 0.7B), 176 tests passing

---

## v0.5.5 — Housekeeping & Foundations 🔥

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | Update README.md | Doc | Fix version badge → v0.5.2, sync pyproject.toml and GitHub release. Add `bitnet_subprocess.py` to structure, update roadmap to v2, add links to new docs. | `README.md`, `pyproject.toml` |
| 2 | Create dedicated ROADMAP.md | Doc | **NEW** — Complete roadmap v2.1 extracted from README. Detailed per version with status, description, deliverables. Becomes the strategic reference document. | `docs/ROADMAP.md` |
| 3 | Create CHANGELOG.md | Doc | **NEW** — Retroactive changelog from v0.1.0 to v0.5.2. Keep a Changelog format. Complete history of 65+ commits. | `CHANGELOG.md` |
| 4 | Redesign website | Web | Update from v0.3.0 → v0.5.2. Add: Desktop App section, download link, new pitch, supported models section, visual roadmap. Updated design. | `index.html` (GitHub Pages) |
| 5 | Update architecture.md | Doc | Add planned Layer 4 (Intelligence): Consensus Inference, Smart Router, ARIA-LM. Add Layer 5 (Economics): $ARIA Token. Mark as "Planned". | `docs/architecture.md` |
| 6 | Start Whitepaper v2 (outline) | Doc | **NEW** — Structured outline of WP v2 covering: extended architecture, Consensus Inference, ARIA-LM, $ARIA tokenomics, agentic app vision. Not full content — just the validated structure. | `docs/whitepaper-v2-outline.md` |
| 7 | Prepare testnet communication strategy | Com | **NEW** — Draft posts: Show HN, r/LocalLLaMA, r/decentralization, Twitter thread. Publication calendar. Angle: new model catalog + extended benchmarks. | `docs/PUBLICATION_POSTS.md` (updated) |
| 8 | **v2.1** — Finalize desktop↔backend integration | Code | Fix /v1/models endpoint (500 error), native subprocess llama-cli integration, functional Live/Mock badge, validated end-to-end test. Eliminate mock responses. **Absolute prerequisite for v0.6.0.** | `aria/api.py`, `desktop/src/hooks/useChat.ts`, `desktop/src/lib/mockResponses.ts` |
| 9 | **v2.1** — Validate Falcon3/Edge model catalog | R&D | Verify on HuggingFace and bitnet.cpp the actual availability of Falcon3 GGUFs (1B/3B/7B/10B) and Falcon-Edge (1B/3B). Test compatibility. If unavailable → Plan B (focus confirmed models, or PT-BitNet conversion). | `docs/models.md` (draft) |

---

## v0.6.0 — Testnet Alpha — Expanded Models + Robust P2P ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | Integrate Falcon3 1.58-bit | Code | **NEW** — Add models validated in v0.5.5 #9 to model_manager.py. GGUF files, bitnet.cpp compatible. Potential catalog of 3 to 9 models (depending on validation). | `aria/model_manager.py`, `tests/` |
| 2 | Integrate Falcon-Edge | Code | **NEW** — Add Falcon-Edge 1B and 3B (natively BitNet, pre-quantized weights). Support community fine-tuning via onebitllms. *Conditioned by v0.5.5 #9 results.* | `aria/model_manager.py`, `docs/models.md` |
| 3 | Update bitnet.cpp | Code | **NEW** — Integrate ELUT parallel kernels from January 2026. +1.15-2.1× additional CPU speedup. Update compilation instructions. | `aria/bitnet_native.py`, `docs/getting-started.md` |
| 4 | Public bootstrap nodes | Infra | Deploy 3-5 bootstrap nodes (lightweight VPS) for initial peer discovery. DNS/network config. Uptime monitoring. | `aria/network.py`, `config/` |
| 5 | Testnet tokens (mock) | Code | **NEW** — Test tokens with no real value to validate reward mechanics. Counters visible in dashboard. Airdrop snapshot preparation. | `aria/node.py`, `aria/ledger.py`, `desktop/` |
| 6 | Desktop App: new model catalog | Code | Update the app's Model Manager with validated models. Download UI, benchmarks displayed per model. | `desktop/src/pages/Models*` |
| 7 | New benchmarks | Code | Benchmark newly integrated models. Publish results. Update website and README with new numbers. | `benchmarks/`, `docs/`, `README.md` |
| 8 | Models documentation | Doc | **NEW** — Create docs/models.md: complete catalog, benchmarks per model, selection guide, Falcon-Edge community fine-tuning. | `docs/models.md` |
| 9 | Testnet launch campaign | Com | Publish posts prepared in v0.5.5. Show HN, r/LocalLLaMA, Twitter thread. Angle: "1-bit models, CPU-only, P2P, join the testnet." | `docs/PUBLICATION_POSTS.md` |
| 10 | **v2.1** — P2P network robustness | Code | NAT traversal (STUN/TURN or hole punching), automatic peer reconnection, production-grade Kademlia DHT, network topology monitoring, firewall handling. **Backbone of the testnet.** | `aria/network.py`, `aria/nat.py` (new), `tests/` |

---

## v0.7.0 — Smart Layer — Reputation + Intelligence ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | Reputation system | Code | Node reliability score (uptime, inference quality, energy honesty). Anti-Sybil: IP limitation + hardware fingerprint. Score published on ledger. | `aria/reputation.py` (new), `aria/proof.py` |
| 2 | Smart Router | Code | **NEW** — Intelligent routing: local 1-bit model by default → if low confidence, escalate to frontier model via user API. Per-response confidence score. Self-improvement. | `aria/router.py` (new), `aria/node.py` |
| 3 | Frontier API overlay | Code | **NEW** — User API key management (Claude, GPT, Grok, Gemini, Mistral). Local encryption. Multi-provider support. API cost counter. | `aria/api_bridge.py` (new), `desktop/src/pages/Settings*` |
| 4 | Intelligent Desktop chat | Code | **NEW** — Chat screen redesign: integrated Smart Router, "local" vs "API" indicator, contextual conversation, local history. First step toward agentic app. | `desktop/src/pages/Chat*` |
| 5 | Airdrop snapshot | Infra | **NEW** — Snapshot of testnet contributions: uptime, inferences, energy. Base for future early adopter airdrop (10% of $ARIA supply). | `aria/ledger.py`, `scripts/` |
| 6 | New features documentation | Doc | Create: docs/smart-router.md, docs/api-bridge.md, docs/reputation.md. Update threat-model.md with new attack surfaces. | `docs/*.md` |

---

## v0.7.5 — R&D + Documentation — Whitepaper v2 & Vision ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | PT-BitNet prototype | R&D | **NEW** — Ternarize Qwen3-14B (28 GB → ~3 GB). Benchmark quality vs full precision. Validate distribution across 3-4 nodes with pipeline parallelism. | `aria/model_manager.py`, `benchmarks/` |
| 2 | Accessibility Tree (Computer Use Level 1) | R&D | **NEW** — Prototype: read OS accessibility tree (UI Automation / AT-SPI) via Tauri/Rust. Convert to text for LLM. First Computer Use building block. | `desktop/src-tauri/src/accessibility.rs` (new) |
| 3 | Write Whitepaper v2 | Doc | **NEW** — Complete WP v2: extended architecture (5 layers), Consensus Inference, ARIA-LM, $ARIA tokenomics, agentic app vision, competitor comparison. PDF + website. | `ARIA_Whitepaper_v2.pdf`, `docs/` |
| 4 | Website redesign v2 | Web | **NEW** — New landing page: "local Claude Desktop" pitch, ARIA-LM section, tokenomics, visual roadmap, download page. Multi-page. | GitHub Pages (complete redesign) |

---

## v0.8.0 — Collective Intelligence — Consensus Inference + Agentic App ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | Consensus Inference Protocol | Code | **NEW** — Full implementation: Phase 1 (Parallel brainstorm), Phase 2 (Iterative deliberation, 1-3 rounds), Phase 3 (Consensus + synthesis). Complete provenance recording on ledger. | `aria/consensus.py` (new), `aria/node.py`, `aria/ledger.py` |
| 2 | Consensus UI parameters | Code | **NEW** — Desktop: choice of agent count (3/5/7), rounds (1-3), Speed/Quality mode, energy budget. Real-time debate visualization. | `desktop/src/pages/Chat*`, `desktop/src/components/` |
| 3 | Local RAG | Code | **NEW** — Local document indexing (PDF, TXT, MD, DOCX). Local embedding (small model via candle/Rust or sentence-transformers). Context injection into prompts. 100% local. | `aria/rag.py` (new), `desktop/src-tauri/src/indexer.rs` (new) |
| 4 | ARIA Code (local sandbox) | Code | **NEW** — Coding assistant mode: read/write/execute code in isolated sandbox (Docker or venv). Automatic error iteration. Free and unlimited. | `aria/code_sandbox.py` (new), `desktop/src/pages/Code*` (new) |
| 5 | Local vision pipeline (Level 2) | Code | **NEW** — OCR (Tesseract/PaddleOCR) + UI detection (OmniParser/Florence-2) + conversion to structured text for LLM. Replaceable module. <1 GB total. | `aria/vision/` (new directory) |
| 6 | Distillation API frontier → training | Code | **NEW** — Pipeline: prompt → frontier API (user key) → high-quality response → local gradient computation → network aggregation. Only the gradient leaves the node. Rewards 15-20× base. | `aria/distillation.py` (new), `aria/api_bridge.py` |
| 7 | Consensus Inference documentation | Doc | **NEW** — Complete spec: docs/consensus-inference.md. Protocol, messages, scoring, provenance, parameters. Update protocol-spec.md and threat-model.md. | `docs/consensus-inference.md` (new), `docs/protocol-spec.md` |
| 8 | WP v2 publication + posts | Com | Publish Whitepaper v2 (arXiv if possible). Dedicated posts: Consensus Inference demo on HN, r/MachineLearning. Technical Twitter thread. | `ARIA_Whitepaper_v2.pdf`, `docs/PUBLICATION_POSTS.md` |

---

## v0.9.0 — ARIA-LM v0 + Ecosystem — Community Fine-tune + MCP ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | **v2.1** — ARIA-LM v0 — Community LoRA fine-tune | Code | LoRA/QLoRA fine-tune of an existing 1-bit model (Falcon-Edge 3B or BitNet-2B) with best Consensus Inference responses + community data. **Not training from scratch — realistic for a solo dev.** Off-peak network hours. | `aria/training/` (new directory), `aria/aria_lm.py` (new) |
| 2 | **v2.1** — Feedback → fine-tune pipeline | Code | User feedback (thumbs up/down) → local dataset → periodic fine-tune. Data never leaves the node. Aggregation of best datasets on the network. Replaces the initially planned full "Federated Learning". | `aria/feedback.py` (new), `aria/training/` |
| 3 | Specialized ARIA-LM variants | Code | **NEW** — ARIA-LM Base (generalist), ARIA-LM Code (programming), ARIA-LM Chat (conversation). Fine-tuning directed by specialized distillation data. | `aria/aria_lm.py`, `aria/model_manager.py` |
| 4 | MCP client (Model Context Protocol) | Code | **NEW** — MCP protocol client implementation in ARIA. Compatible with all existing MCP servers (GitHub, Slack, Google Drive, DB, etc.). | `aria/mcp_client.py` (new), `desktop/src-tauri/` |
| 5 | Piloted browser (ARIA Browse) | Code | **NEW** — Integrated WebView or Playwright headless driven by LLM. Web search, form filling, data extraction. Controlled by Smart Router. | `desktop/src/pages/Browse*` (new), `aria/browser.py` (new) |
| 6 | Consensus → ARIA-LM synergy | Code | **NEW** — Best Consensus Inference responses automatically feed ARIA-LM fine-tuning. Self-improving loop. Quality scoring of consensus responses. | `aria/consensus.py`, `aria/training/` |
| 7 | Mobile (design & prototype) | Design | Mobile UI/UX design. React Native or Tauri Mobile prototype. On-device inference for small models (1B-3B). No full release — R&D. | `mobile/` (new directory) |
| 8 | ARIA-LM + MCP documentation | Doc | **NEW** — Create: docs/aria-lm.md (architecture, fine-tune, feedback loop), docs/mcp-integration.md, docs/browser-agent.md. Update architecture.md. | `docs/*.md` |

---

## v1.0.0 — Mainnet — $ARIA Token + DAO + Production ⬜

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | $ARIA Token — Smart contract + deployment | Code | **NEW** — Deploy on Base/Arbitrum (L2). Fixed supply 1 billion. 2% burn mechanism. Audited smart contracts. Distribution: 50% mining / 20% DAO / 15% team / 10% testnet / 5% eco. | `contracts/` (new), `aria/token.py` (new) |
| 2 | Hybrid blockchain — Bridge ledger → L2 | Code | **NEW** — Internal ARIA ledger (fast free micro-transactions) + periodic L2 settlement (liquidity/exchanges). Lightning Network model. | `aria/ledger.py`, `aria/bridge.py` (new) |
| 3 | Multi-tier rewards | Code | **NEW** — Dynamic pricing (supply/demand). 6 tiers: inference (1×), consensus (3-5×), training (10×), distillation API (15-20×), feedback (0.1×), hosting (passive). | `aria/economics.py` (new), `aria/node.py` |
| 4 | DAO & governance | Code | **NEW** — Quadratic voting. On-chain proposals and votes. DAO treasury control (200M $ARIA). Voting interface in desktop app. | `contracts/governance/`, `desktop/src/pages/DAO*` (new) |
| 5 | Early adopter airdrop | Infra | **NEW** — Distribution of 100M $ARIA to testnet early adopters, proportional to v0.7.0 snapshot. Claim via desktop app. | `contracts/`, `desktop/` |
| 6 | Staking + slashing | Code | **NEW** — Mandatory staking for validators. Slashing for cheating (data poisoning, fake energy). Integrated with v0.7.0 reputation system. | `contracts/`, `aria/reputation.py` |
| 7 | Tokenomics documentation | Doc | **NEW** — docs/tokenomics.md: supply, distribution, mechanisms, rewards, burn, staking, DAO. Separate from whitepaper for quick reference. | `docs/tokenomics.md` (new) |
| 8 | Security audit | Infra | Smart contract audit by third-party firm. P2P network audit. Update threat-model.md with results. Bug bounty program. | `docs/threat-model.md`, `docs/audit-report.md` (new) |
| 9 | Launch + communication campaign | Com | Mainnet campaign: HN, Reddit, Twitter, LinkedIn, Product Hunt. DEX listings (Uniswap/Aerodrome). Press kit, demo video, complete documentation. | `docs/PUBLICATION_POSTS.md`, `press-kit/` (new) |

---

## v1.1.0+ — Beyond — Long-term Vision 🔮

| # | Task | Type | Detail | Files |
|---|------|------|--------|-------|
| 1 | Mobile app iOS/Android | Code | Full mobile app release. On-device inference (1B-3B). Lightweight mobile node. Network contribution from smartphone. | `mobile/` |
| 2 | Full Computer Use (Level 2+3) | Code | **MOVED** — Full local vision pipeline + frontier routing for complex tasks. Mouse/keyboard control via enigo (Rust). Improvement feedback loop. *Moved from v1.0.0 to keep mainnet focused.* | `desktop/src-tauri/src/computer_use.rs` (new) |
| 3 | ARIA-LM vN — Distillation + Federated Learning | R&D | **v2.1** — The real ARIA-LM: 3B training by multi-teacher distillation + federated RLHF (Flower) + Consensus data. ARIA-LM starts rivaling its teachers. **When community and resources allow.** | `aria/training/`, `aria/federated.py` (new) |
| 4 | MoE + 1-bit R&D | R&D | **NEW** — 100B+ total model, 5-10B active/token, ~1 GB memory. Frontier-class distributed on laptops. Building blocks: QuEST W1A1, Spectra scaling laws. | `research/` (new) |
| 5 | Native 1-bit VLM | R&D | **NEW** — If the modular vision pipeline proves insufficient: ternarize a small VLM (Moondream, Florence-2) via PT-BitNet. Native vision integrated into LLM. | `aria/vision/` |
| 6 | Third-party developer SDK | Code | **NEW** — SDK for third-party developers to build apps on the ARIA network. Stable API, documentation, examples, templates. | `sdk/` (new), `docs/developer-guide.md` |
| 7 | ARIA-LM Convergence | R&D | **NEW** — Continuous loop: distillation + federated RLHF + Consensus data. Versions snapshotted on ledger. Goal: autonomous community model. | `aria/training/` |

---

## Summary

| Metric | Value |
|--------|-------|
| Planned versions | 9 |
| Identified tasks | 62 |
| New tasks (vs v1) | 44 |
| v2.1 corrections | 7 |

---

*ARIA Protocol — Autonomous Responsible Intelligence Architecture*
*Roadmap v2.1 · Updated February 6, 2026 · Anthony MURGO*
*Based on: Brainstorming Session + GitHub Repo Audit + ARIA Protocol Conversations 1-7*
