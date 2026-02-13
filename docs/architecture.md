# ARIA Protocol Architecture

This document describes the technical architecture of the ARIA Protocol, a peer-to-peer network for distributed AI inference.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARIA PROTOCOL v0.5.5                               │
│                  Distributed AI Inference Network                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      LAYER 3: SERVICE                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │   OpenAI    │  │    Web      │  │    CLI      │                  │   │
│  │  │  API Server │  │  Dashboard  │  │  Interface  │                  │   │
│  │  │  (aiohttp)  │  │  (realtime) │  │  (argparse) │                  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │   │
│  └─────────┼────────────────┼────────────────┼──────────────────────────┘   │
│            │                │                │                              │
│            └────────────────┼────────────────┘                              │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 2: CONSENSUS                                │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │   Provenance    │  │  Proof of       │  │  Proof of       │      │   │
│  │  │   Ledger        │  │  Useful Work    │  │  Sobriety       │      │   │
│  │  │  (provenance)   │  │ (useful work)   │  │ (energy track)  │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │   │
│  │           │                    │                    │                │   │
│  │           └────────────────────┼────────────────────┘                │   │
│  │                                ▼                                     │   │
│  │            ┌─────────────────────────────────────┐                   │   │
│  │            │        Consent Contracts            │                   │   │
│  │            │  (resource limits, schedules)       │                   │   │
│  │            └──────────────────┬──────────────────┘                   │   │
│  └───────────────────────────────┼──────────────────────────────────────┘   │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      LAYER 1: COMPUTE                                │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │   P2P Network   │  │   Inference     │  │  Model Shard    │      │   │
│  │  │   (WebSocket)   │  │   Engine        │  │  Distribution   │      │   │
│  │  │                 │  │  (1-bit/ternary)│  │                 │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │   │
│  │           │                    │                    │                │   │
│  │           └────────────────────┴────────────────────┘                │   │
│  │                                │                                     │   │
│  │                    ┌───────────┴───────────┐                         │   │
│  │                    │   ARIANode Core       │                         │   │
│  │                    │   (orchestration)     │                         │   │
│  │                    └───────────────────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### Layer 1: Compute Layer

The foundation of ARIA, handling actual inference computation and network communication.

#### P2P Network (`network.py`)

- **Technology**: Real WebSocket connections using `websockets` library
- **Discovery**: Peer announcement and routing table management
- **Heartbeat**: 30-second ping/pong intervals for peer health monitoring
- **Dead Peer Detection**: Automatic pruning after 5 minutes of inactivity

```
┌──────────────────────────────────────────────────────────────┐
│                    P2P Network Topology                      │
│                                                              │
│     ┌─────────┐         ┌─────────┐         ┌─────────┐     │
│     │ Node A  │◄───────►│ Node B  │◄───────►│ Node C  │     │
│     │ :8765   │         │ :8766   │         │ :8767   │     │
│     └────┬────┘         └────┬────┘         └────┬────┘     │
│          │                   │                   │           │
│          │    ┌──────────────┴──────────────┐    │           │
│          └───►│          Node D             │◄───┘           │
│               │          :8768              │                │
│               └─────────────────────────────┘                │
│                                                              │
│  Each node maintains WebSocket connections to all peers      │
└──────────────────────────────────────────────────────────────┘
```

#### Inference Engine (`inference.py`)

- **Model Type**: Ternary weights (-1, 0, +1)
- **Memory Efficiency**: 1.58 bits per weight (vs 16-32 bits for standard models)
- **Operations**: Pure addition/subtraction (no multiplication)
- **Energy**: ~0.001 mJ per 1000 ternary operations

```
┌────────────────────────────────────────────────────────────┐
│               1-Bit Inference Pipeline                      │
│                                                             │
│  Input: "What is AI?"                                       │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │   Tokenizer     │  [87, 104, 97, 116, 32, ...]          │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │  Embedding      │  → Initial activations (512-dim)       │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │  TernaryLayer 0 │  W ∈ {-1, 0, +1}                       │
│  │  (no multiply!) │  y = Σ(x where W=1) - Σ(x where W=-1)  │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│      ... N layers ...                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │  Generator      │  → Token IDs                           │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │  Detokenizer    │  → Output text                         │
│  └─────────────────┘                                        │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

#### Inference Backends

ARIA supports multiple inference backends with automatic fallback:

```
┌─────────────────────────────────────────────────────────────┐
│                  Backend Selection (auto mode)               │
│                                                              │
│  Priority 1: Native DLL (bitnet.cpp ctypes)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BitNetNative — Direct ctypes bindings to bitnet.dll   │   │
│  │ ✓ Fastest option (in-process, zero IPC overhead)      │   │
│  │ ✗ Requires compiled bitnet.dll/libbitnet.so            │   │
│  └──────────────────────────────────────────────────────┘   │
│              │ unavailable? ▼                                │
│  Priority 2: Subprocess (llama-cli.exe)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BitNetSubprocess — Calls llama-cli.exe as subprocess  │   │
│  │ ✓ Real 1-bit inference on CPU                         │   │
│  │ ✓ Works with standard bitnet.cpp builds               │   │
│  │ ✓ Parses perf stats from stderr                       │   │
│  │ ✗ Subprocess overhead (~50-100ms per call)             │   │
│  └──────────────────────────────────────────────────────┘   │
│              │ unavailable? ▼                                │
│  Priority 3: Simulation (reference implementation)           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ TernaryLayer simulation — Protocol mechanics demo     │   │
│  │ ✓ Always available, no dependencies                   │   │
│  │ ✓ Full protocol flow (ledger, proofs, scoring)        │   │
│  │ ✗ No real language model output                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  CLI: aria node start --backend auto|native|subprocess|sim  │
└─────────────────────────────────────────────────────────────┘
```

| Backend | Module | Real Inference | Dependencies | Overhead |
|---------|--------|---------------|--------------|----------|
| native | bitnet_native.py | Yes | bitnet.dll / libbitnet.so | None (in-process) |
| subprocess | bitnet_subprocess.py | Yes | llama-cli.exe (bitnet.cpp) | ~50-100ms IPC |
| simulation | inference.py | No | None | None |

#### Model Sharding

Models are split across multiple nodes for distributed inference:

```
┌───────────────────────────────────────────────────────────────┐
│              Model Sharding (24-layer model)                  │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │    Node Alice   │  │    Node Bob     │  │   Node Carol    ││
│  │   Layers 0-7    │  │   Layers 8-15   │  │  Layers 16-23   ││
│  │   (~133MB)      │  │   (~133MB)      │  │   (~133MB)      ││
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘│
│           │                    │                    │          │
│           └────────────────────┴────────────────────┘          │
│                                │                               │
│                    Total: ~400MB (2B params)                   │
│                   vs 4GB for FP16 equivalent                   │
└───────────────────────────────────────────────────────────────┘
```

### Layer 2: Consensus Layer

Ensures transparency, accountability, and quality tracking.

#### Provenance Ledger (`ledger.py`)

An immutable provenance ledger recording all inference operations:

```
┌─────────────────────────────────────────────────────────────┐
│                   Provenance Ledger                          │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐         │
│  │  Block 0   │───►│  Block 1   │───►│  Block 2   │───► ... │
│  │  (genesis) │    │            │    │            │         │
│  └────────────┘    └────────────┘    └────────────┘         │
│                                                              │
│  Each Block Contains:                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │ index: 42                                         │       │
│  │ timestamp: 1706745600                             │       │
│  │ previous_hash: "a1b2c3..."                        │       │
│  │ contributor_id: "node-xyz"                          │       │
│  │ records: [                                        │       │
│  │   {                                               │       │
│  │     query_hash: "sha256...",                      │       │
│  │     output_hash: "sha256...",                     │       │
│  │     model_id: "aria-2b-1bit",                     │       │
│  │     node_ids: ["alice", "bob", "carol"],          │       │
│  │     energy_mj: 28.5,                              │       │
│  │     latency_ms: 1250,                             │       │
│  │     tokens_generated: 50                          │       │
│  │   },                                              │       │
│  │   ...                                             │       │
│  │ ]                                                 │       │
│  │ nonce: 12847                                      │       │
│  │ hash: "00abc..."  (difficulty=2 leading zeros)   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Key Property: NO model weights on-ledger, only metadata     │
└─────────────────────────────────────────────────────────────┘
```

#### Proof of Useful Work (`proof.py`)

Unlike traditional wasteful hash computation, ARIA ensures every computation is useful AI inference:

```
┌─────────────────────────────────────────────────────────────┐
│                  Proof of Useful Work                        │
│                                                              │
│    Bitcoin                         ARIA                      │
│    ───────                         ────                      │
│    hash(nonce) → nothing useful    inference(query) → real AI output │
│    Wasted energy                   Actual AI work            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ UsefulWorkProof:                                      │   │
│  │   node_id: "alice"                                    │   │
│  │   inference_id: "inf-123"                             │   │
│  │   query_hash: "sha256..."   (privacy preserved)       │   │
│  │   output_hash: "sha256..."                            │   │
│  │   model_id: "aria-2b-1bit"                            │   │
│  │   energy_mj: 28.0                                     │   │
│  │   latency_ms: 1200                                    │   │
│  │   timestamp: 1706745600                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Top Contributor Tracking:                                   │
│  - Track verified work count per node per epoch              │
│  - Nodes are ranked by quality and quantity of useful work   │
│  - Used for reputation scoring and network quality metrics   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Proof of Sobriety (`proof.py`)

Verifiable energy efficiency attestations:

```
┌─────────────────────────────────────────────────────────────┐
│                   Proof of Sobriety                          │
│                                                              │
│  Energy Measurement:                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Linux: Intel RAPL counters                            │   │
│  │   /sys/class/powercap/intel-rapl:0/energy_uj         │   │
│  │                                                       │   │
│  │ Fallback: Estimation based on BitNet benchmarks       │   │
│  │   energy = (inferences × 28mJ) + (time × 5W × 10%)   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Efficiency Rating:                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  A+ (< 30 mJ/inference)   - Exceptional               │   │
│  │  A  (30-50 mJ/inference)  - Excellent                 │   │
│  │  B  (50-100 mJ/inference) - Good                      │   │
│  │  C  (100-150 mJ/inference)- Average (GPU baseline)    │   │
│  │  D  (> 150 mJ/inference)  - Below average             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Network Savings vs GPU:                                     │
│  - GPU baseline: 150 mJ per inference                        │
│  - ARIA target: 20-50 mJ per inference                       │
│  - CO2 saved: ~0.4g per kJ                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Consent Contracts (`consent.py`)

No resource is used without explicit permission:

```
┌─────────────────────────────────────────────────────────────┐
│                    Consent Contract                          │
│                                                              │
│  ARIAConsent {                                               │
│    // Resource Limits                                        │
│    cpu_percent: 25,           // Max 25% CPU usage           │
│    max_ram_mb: 512,           // Max 512MB RAM               │
│    max_bandwidth_mbps: 10,    // Max 10 Mbps network         │
│                                                              │
│    // Availability                                           │
│    schedule: "08:00-22:00",   // Available hours (UTC)       │
│    days: ["mon", "tue", "wed", "thu", "fri"],                │
│                                                              │
│    // Task Preferences                                       │
│    task_types: [TEXT_GENERATION, CODE_GENERATION],           │
│    max_concurrent_tasks: 2,                                  │
│                                                              │
│    // Privacy                                                │
│    allow_logging: true,                                      │
│    allow_geo_tracking: false,                                │
│                                                              │
│    // Quality                                               │
│    min_reputation_score: 0.001  // Minimum reputation threshold │
│  }                                                           │
│                                                              │
│  Consent Matching:                                           │
│  request.matches(consent) → bool                             │
│  - Checks schedule availability                              │
│  - Verifies task type is accepted                            │
│  - Ensures resource requirements fit limits                  │
│  - Confirms contribution score meets minimum threshold       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Layer 3: Service Layer

Provides user-facing interfaces and integrations.

#### OpenAI-Compatible API (`api.py`)

```
┌─────────────────────────────────────────────────────────────┐
│               OpenAI-Compatible API Server                   │
│                                                              │
│  POST /v1/chat/completions                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Request:                                              │   │
│  │ {                                                     │   │
│  │   "model": "aria-2b-1bit",                           │   │
│  │   "messages": [                                       │   │
│  │     {"role": "user", "content": "Hello!"}            │   │
│  │   ],                                                  │   │
│  │   "max_tokens": 100,                                  │   │
│  │   "stream": false                                     │   │
│  │ }                                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ARIAOpenAIServer                                      │   │
│  │   → Connects to ARIA node via WebSocket               │   │
│  │   → Translates to inference_request                   │   │
│  │   → Receives result                                   │   │
│  │   → Formats as OpenAI response                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Response:                                             │   │
│  │ {                                                     │   │
│  │   "id": "chatcmpl-aria-...",                         │   │
│  │   "choices": [{                                       │   │
│  │     "message": {                                      │   │
│  │       "role": "assistant",                            │   │
│  │       "content": "Hello! How can I help?"            │   │
│  │     },                                                │   │
│  │     "finish_reason": "stop"                           │   │
│  │   }],                                                 │   │
│  │   "usage": {                                          │   │
│  │     "prompt_tokens": 10,                              │   │
│  │     "completion_tokens": 15,                          │   │
│  │     "total_tokens": 25                                │   │
│  │   }                                                   │   │
│  │ }                                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Web Dashboard (`dashboard.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                   Real-Time Dashboard                        │
│                   http://localhost:8080                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │  Node Status      │  │  Network Stats    │               │
│  │  ─────────────    │  │  ─────────────    │               │
│  │  ID: alice        │  │  Peers: 3         │               │
│  │  Uptime: 2h 15m   │  │  Messages: 1,247  │               │
│  │  Inferences: 42   │  │  Requests: 89     │               │
│  │  Score: 0.042     │  │                   │               │
│  └───────────────────┘  └───────────────────┘               │
│                                                              │
│  ┌───────────────────────────────────────────┐              │
│  │  Energy Savings                            │              │
│  │  ─────────────────                         │              │
│  │  Total Energy: 1.23 J                      │              │
│  │  GPU Equivalent: 6.30 J                    │              │
│  │  Savings: 80.5%                            │              │
│  │  CO2 Saved: 2.03 g                         │              │
│  └───────────────────────────────────────────┘              │
│                                                              │
│  ┌───────────────────────────────────────────┐              │
│  │  Recent Inferences                         │              │
│  │  ─────────────────                         │              │
│  │  • "What is quantum..." - 1.2s - 28mJ     │              │
│  │  • "Explain machine..." - 0.9s - 25mJ     │              │
│  │  • "Write a function..." - 1.5s - 32mJ    │              │
│  └───────────────────────────────────────────┘              │
│                                                              │
│  WebSocket: Real-time updates pushed to all clients          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## End-to-End Inference Flow

Here's how a request flows through the entire system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    END-TO-END INFERENCE FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CLIENT REQUEST                                                          │
│  ┌──────────────────┐                                                       │
│  │  OpenAI Client   │ POST /v1/chat/completions                             │
│  │  or curl         │ {"model": "aria-2b-1bit", "messages": [...]}         │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ▼                                                                 │
│  2. API SERVER                                                              │
│  ┌──────────────────┐                                                       │
│  │  ARIAOpenAIServer│ Validates request, connects to ARIA node              │
│  │  :3000           │ Sends inference_request via WebSocket                 │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ▼                                                                 │
│  3. ARIA NODE (Entry Point)                                                 │
│  ┌──────────────────┐                                                       │
│  │  ARIANode        │ Receives request, checks consent                      │
│  │  (Alice)         │ Decides: local or distributed inference?              │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ├──────────────────────────────────────────┐                      │
│           ▼ (Local)                                  ▼ (Distributed)        │
│  4a. LOCAL INFERENCE                        4b. DISTRIBUTED PIPELINE        │
│  ┌──────────────────┐                       ┌──────────────────────────┐   │
│  │ InferenceEngine  │                       │ build_pipeline_chain()   │   │
│  │ - Load model     │                       │ - Find nodes with shards │   │
│  │ - Run layers     │                       │ - Order by layer_start   │   │
│  │ - Generate output│                       │ - Create pipeline        │   │
│  └────────┬─────────┘                       └───────────┬──────────────┘   │
│           │                                             │                   │
│           │                                             ▼                   │
│           │                       ┌────────────────────────────────────┐   │
│           │                       │  Pipeline Execution:               │   │
│           │                       │                                    │   │
│           │                       │  Alice          Bob          Carol │   │
│           │                       │  (L0-7)   →   (L8-15)   →  (L16-23)│   │
│           │                       │    │            │             │    │   │
│           │                       │    ▼            ▼             ▼    │   │
│           │                       │  process    process       process  │   │
│           │                       │  stage      stage         stage    │   │
│           │                       │    │            │             │    │   │
│           │                       │  [activations forwarded via WS]   │   │
│           │                       │                               │    │   │
│           │                       │                               ▼    │   │
│           │                       │                        final result│   │
│           │                       └────────────────────────────────────┘   │
│           │                                             │                   │
│           ▼                                             ▼                   │
│  5. RECORD ON LEDGER                                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ ProvenanceLedger.add_record({                                         │  │
│  │   query_hash, output_hash, model_id, node_ids, energy_mj, latency_ms │  │
│  │ })                                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│           │                                                                 │
│           ▼                                                                 │
│  6. SUBMIT PROOF OF USEFUL WORK                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ ProofOfUsefulWork.submit_proof(UsefulWorkProof(...))                  │  │
│  │ → Verified work count incremented                                     │  │
│  │ → Node contribution tracked for reputation                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│           │                                                                 │
│           ▼                                                                 │
│  7. UPDATE CONTRIBUTION SCORE                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ score = base_rate × quality_score × efficiency_bonus                  │  │
│  │                                                                       │  │
│  │ base_rate = 0.001 (contribution points)                               │  │
│  │ quality = 1 - (latency - 1000ms) / 4000ms    [0, 1]                  │  │
│  │ efficiency = min(2.0, max(0.5, 150mJ / energy))   [0.5, 2.0]         │  │
│  │                                                                       │  │
│  │ Contribution score is used for reputation tracking,                   │  │
│  │ not as a currency or token.                                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│           │                                                                 │
│           ▼                                                                 │
│  8. RETURN RESPONSE                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ InferenceResult → OpenAI format → HTTP Response → Client             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## WebSocket Message Protocol

All node-to-node communication uses a JSON-based WebSocket protocol:

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `ping` | A → B | Heartbeat check |
| `pong` | B → A | Heartbeat response |
| `peer_announce` | A → All | New peer joining network |
| `shard_announce` | A → All | Node declares available model shards |
| `inference_request` | A → B | Request inference from peer |
| `inference_response` | B → A | Return inference result |
| `pipeline_forward` | A → B | Forward activations to next pipeline stage |
| `get_peers` | A → B | Request peer list |
| `peers_list` | B → A | Return list of known peers |
| `get_stats` | A → B | Request node statistics |
| `stats` | B → A | Return node statistics |

### Message Format

```json
{
  "type": "inference_request",
  "request_id": "req-abc123",
  "data": {
    "query": "What is quantum computing?",
    "model_id": "aria-2b-1bit",
    "max_tokens": 100
  },
  "timestamp": 1706745600,
  "sender": "node-alice"
}
```

### Pipeline Forward Message

```json
{
  "type": "pipeline_forward",
  "request_id": "req-abc123",
  "data": {
    "state": {
      "request_id": "req-abc123",
      "model_id": "aria-2b-1bit",
      "query": "What is AI?",
      "activation_b64": "base64-encoded-activation-data...",
      "current_layer": 8,
      "total_layers": 24
    },
    "replicas": ["node-bob-backup"]
  },
  "timestamp": 1706745601,
  "sender": "node-alice"
}
```

### Connection Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│                WebSocket Connection Lifecycle                 │
│                                                               │
│  1. CONNECT                                                   │
│     ws://peer-host:8765                                       │
│                                                               │
│  2. ANNOUNCE                                                  │
│     → peer_announce { node_id, host, port, consent }          │
│     ← peer_announce (from other node)                         │
│                                                               │
│  3. SHARD REGISTRATION (if has model)                         │
│     → shard_announce { model_id, layer_start, layer_end }     │
│                                                               │
│  4. HEARTBEAT LOOP (every 30s)                                │
│     → ping                                                    │
│     ← pong                                                    │
│     (if no pong in 300s, mark peer as dead)                   │
│                                                               │
│  5. NORMAL OPERATION                                          │
│     ←→ inference_request / inference_response                 │
│     ←→ pipeline_forward                                       │
│     ←→ get_stats / stats                                      │
│                                                               │
│  6. DISCONNECT                                                │
│     Connection closed, peer removed from routing table        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT DEPENDENCY GRAPH                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          ┌─────────────┐                                    │
│                          │   cli.py    │                                    │
│                          │  (commands) │                                    │
│                          └──────┬──────┘                                    │
│                                 │                                           │
│           ┌─────────────────────┼─────────────────────┐                     │
│           │                     │                     │                     │
│           ▼                     ▼                     ▼                     │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐              │
│   │   api.py      │    │  dashboard.py │    │   node.py     │              │
│   │ (HTTP server) │    │  (web UI)     │    │  (core node)  │              │
│   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘              │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │                                            │
│                                ▼                                            │
│                       ┌───────────────┐                                     │
│                       │  network.py   │                                     │
│                       │   (P2P)       │                                     │
│                       └───────┬───────┘                                     │
│                               │                                             │
│        ┌──────────────────────┼──────────────────────┐                      │
│        │                      │                      │                      │
│        ▼                      ▼                      ▼                      │
│  ┌───────────┐         ┌───────────┐         ┌───────────┐                 │
│  │inference.py│         │ ledger.py │         │ consent.py│                 │
│  │ (engine)  │         │(provenance)│         │(contracts)│                 │
│  └─────┬─────┘         └─────┬─────┘         └───────────┘                 │
│        │                     │                                              │
│   ┌────┴─────┐               ▼                                              │
│   │          │         ┌───────────┐                                        │
│   ▼          ▼         │ proof.py  │                                        │
│ ┌──────┐ ┌──────────┐ │(PoUW/PoS) │                                        │
│ │bitnet│ │bitnet_   │ └───────────┘                                        │
│ │native│ │subprocess│                                                       │
│ └──────┘ └──────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
aria-protocol/
├── aria/
│   ├── __init__.py          # Package exports, __version__
│   ├── node.py              # ARIANode - main orchestrator
│   ├── network.py           # ARIANetwork - P2P WebSocket layer
│   ├── inference.py         # InferenceEngine, TernaryLayer, ModelShard
│   ├── bitnet_native.py     # Native ctypes bindings to bitnet.cpp
│   ├── bitnet_subprocess.py # Subprocess backend using llama-cli
│   ├── model_manager.py     # ModelManager - GGUF model download/cache
│   ├── ledger.py            # ProvenanceLedger, Block, InferenceRecord
│   ├── proof.py             # ProofOfUsefulWork, ProofOfSobriety
│   ├── consent.py           # ARIAConsent, TaskType
│   ├── cli.py               # Command-line interface
│   ├── api.py               # OpenAI-compatible HTTP API
│   └── dashboard.py         # Real-time web dashboard
├── tests/
│   ├── test_node.py
│   ├── test_inference.py
│   ├── test_ledger.py
│   ├── test_proof.py
│   ├── test_consent.py
│   ├── test_api_models.py
│   ├── test_bitnet_native.py
│   └── test_bitnet_subprocess.py
├── examples/
│   ├── demo.py              # Full protocol demonstration
│   └── openai_client.py     # OpenAI client example
├── docs/
│   ├── architecture.md      # This document
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── protocol-spec.md
│   ├── threat-model.md
│   └── ROADMAP.md
├── pyproject.toml           # Python package configuration
├── Makefile                 # Build and test commands
└── README.md
```

## Conversation Memory Architecture

ARIA implements a persistent, privacy-first memory system that operates entirely
on the user's device. No conversation data leaves the node.

### Three-Tier Memory Model

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    CONVERSATION MEMORY ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  HOT TIER — Working Context                                        │ │
│  │  Current session messages + injected memories                      │ │
│  │  Storage: in-memory (context window)                               │ │
│  │  Latency: 0ms (already in prompt)                                  │ │
│  └──────────────────────────┬─────────────────────────────────────────┘ │
│                              │ compaction trigger                        │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  WARM TIER — Personal Profile Graph (Kuzu)                         │ │
│  │  Extracted facts, preferences, relationships                       │ │
│  │  Storage: embedded graph DB (Kuzu, ~50MB)                          │ │
│  │  Latency: <40ms (embedding search + graph query)                   │ │
│  │                                                                    │ │
│  │  Node types (13): Person, Fact, Preference, Goal, Project,         │ │
│  │    Communication_Style, Relationship, Event, Skill, Opinion,       │ │
│  │    Habit, Context_Snapshot, Session                                 │ │
│  │                                                                    │ │
│  │  Relation types (9): KNOWS, HAS_PREFERENCE, WORKS_ON,             │ │
│  │    HAS_GOAL, HAS_SKILL, HOLDS_OPINION, RELATED_TO,                │ │
│  │    MENTIONED_IN, HAPPENED_DURING                                   │ │
│  └──────────────────────────┬─────────────────────────────────────────┘ │
│                              │ TTL expiry / cold archival               │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  COLD TIER — Archive                                               │ │
│  │  Full session transcripts, expired facts, audit trail              │ │
│  │  Storage: SQLite + zstd compression                                │ │
│  │  Latency: 50-200ms (decompression + query)                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Memory Compaction Strategy

The transition between memory tiers follows a token-budget compaction model,
validated by prior work (MemGPT [Packer et al., ICLR 2024], LangChain
ConversationSummaryBufferMemory):

- **Trigger**: When the Hot tier exceeds a configurable token threshold
  (default: 75% of model context length), oldest messages are compacted.
- **Compaction method**: A lightweight model (Qwen2.5-1.5B Q4_K_M) generates
  structured summaries asynchronously to avoid blocking inference.
- **Output**: Compacted summaries stored as Warm-tier facts in the Profile Graph
  with source attribution and confidence scores.
- **Cold archival**: Warm facts older than configurable TTL (default: 30 days
  without recall) move to Cold tier, compressed with zstd.
- **Manual override**: Users can pin facts to prevent compaction or force-purge
  via the Memory Manager UI.

References:
- MemGPT: Towards LLMs as Operating Systems (Packer et al., ICLR 2024)
- LangChain ConversationSummaryBufferMemory (docs.langchain.com)

### Cognitive Memory Model — Full Coverage

ARIA's memory architecture maps to all five types of human memory identified
in cognitive science, making it one of the first open-source AI systems to
achieve full cognitive memory coverage:

| Human Memory Type | Function | ARIA Implementation | Status |
|---|---|---|---|
| **Episodic** | Stores experiences with temporal context | Hot tier (context window) + Cold tier (SQLite archive with timestamps, session metadata) | ✅ Designed |
| **Semantic** | Distilled knowledge from many episodes | Warm tier — Personal Profile Graph (Kuzu). Facts extracted and consolidated across sessions. | ✅ Designed |
| **Procedural** | Know-how, learned behaviors | Communication_Style nodes in Profile Graph. Slow-cadence adaptation across sessions (Adaptation Paradox). | ✅ Designed |
| **Working** | Selective attention gating | Embedding-based injection (<40ms budget). E5-small-v2 similarity search selects relevant memories for context. | ✅ Designed |
| **Prospective** | Future-oriented intentions ("remember to do X") | Intention nodes + dual-pathway trigger system (time-based + semantic + condition-based). | 📐 Specified |

No major open-source AI agent framework — including MemGPT/Letta, Mem0, LangChain,
Zep/Graphiti, or Cognee — implements a dedicated prospective memory system with
autonomous intention formation, multi-modal triggers, and intention lifecycle management.

The closest academic work is Tan et al. (2025), which introduces Prospective Reflection — dynamically summarizing interactions into a topic-based memory bank optimized for anticipated future retrieval. While this improves memory organization for future access, it does not implement deferred intention execution with autonomous trigger mechanisms, which is the core of psychological prospective memory and ARIA's implementation.

References:
- Einstein, G.O. & McDaniel, M.A. (2005). Prospective memory: Multiple retrieval processes. *Current Directions in Psychological Science*, 14(6), 286–290.
- Scullin, M.K., McDaniel, M.A. & Shelton, J.T. (2013). The Dynamic Multiprocess Framework. *Cognitive Psychology*, 67(1–2), 55–71.
- Rummel, J. & Kvavilashvili, L. (2023). Current theories of prospective memory. *Nature Reviews Psychology*, 2, 40–54.
- Tan, W. et al. (2025). In Prospect and Retrospect: Reflective Memory Management for Long-term Personalized Dialogue Agents. ACL 2025. arXiv:2503.08026. — Introduces Prospective Reflection for topic-based memory organization optimized for future retrieval. Closest existing work to prospective memory for LLM agents, achieving >10% accuracy improvement on LongMemEval. Addresses memory organization for anticipated retrieval, not deferred intention execution (which ARIA implements).

### Prospective Memory Architecture

Prospective memory is the cognitive faculty for remembering to carry out intended
actions in the future. ARIA implements this via a dual-pathway architecture inspired
by Einstein & McDaniel's Multiprocess Framework.

#### Intention Node Schema

A new node type `Intention` (14th type) is added to the Personal Profile Graph:

```
(:Intention {
    id: STRING,                  -- Unique identifier
    content: STRING,             -- "Ask about presentation results"
    trigger_type: STRING,        -- "time" | "semantic" | "condition" | "session_start"
    trigger_condition: STRING,   -- ISO datetime | topic keywords | expression | "*"
    trigger_embedding: FLOAT[],  -- Pre-computed embedding for semantic matching
    priority: FLOAT,             -- 0.0 to 1.0 (base priority)
    created_at: TIMESTAMP,
    expires_at: TIMESTAMP,       -- TTL, NULL = never expires
    status: STRING,              -- "pending" | "triggered" | "executed" | "expired" | "cancelled"
    fire_count: INT,             -- Times triggered (for recurring intentions)
    max_fires: INT,              -- 1 = one-shot, -1 = unlimited recurring
    source_session: STRING,      -- Session where intention was created
    confidence: FLOAT,           -- Extraction confidence (heuristic vs LLM)
    context_summary: STRING      -- Compressed context for token-efficient injection
})
```

New relationships:

```
(:Person)-[:HAS_INTENTION]->(:Intention)
(:Intention)-[:RELATES_TO]->(:Project | :Person | :Goal | :Fact)
(:Session)-[:CREATED_INTENTION]->(:Intention)
(:Intention)-[:DEPENDS_ON]->(:Intention)  -- Dependency chains
```

#### Dual-Pathway Trigger System

Inspired by the neural architecture of prospective memory (rostral prefrontal
cortex for strategic monitoring, hippocampus for spontaneous retrieval):

**Pathway 1 — Strategic Monitoring (Time-based, polling)**

For time-based and session-start intentions. A lightweight scheduler checks
pending intentions against temporal conditions:

- On session start: query all `trigger_type = 'session_start'` or overdue time triggers
- Periodic check: poll time-based intentions every N messages (adaptive frequency)
- Budget: ~3ms per check via Kuzu indexed query

```cypher
MATCH (p:Person)-[:HAS_INTENTION]->(i:Intention)
WHERE i.status = 'pending'
  AND (i.trigger_type = 'session_start'
       OR (i.trigger_type = 'time' AND i.trigger_condition <= datetime()))
RETURN i ORDER BY i.priority DESC LIMIT 3
```

**Pathway 2 — Spontaneous Retrieval (Semantic, embedding-based)**

For event-based and topic-based intentions. When new user input arrives, its
embedding is compared against all active intention trigger embeddings:

- Compute input embedding via E5-small-v2 (~5ms, already in pipeline)
- ANN search against intention trigger embeddings (~2ms for <1000 intentions)
- Fire intentions exceeding similarity threshold (configurable, default 0.78)
- Cooldown period prevents rapid re-firing (default: 1 per session per intention)

This pathway has near-zero ongoing cost — it piggybacks on the existing embedding
computation in the memory recall pipeline.

**Pathway 3 — Condition Triggers (State-based)**

For activity-based intentions triggered by state changes:

- Register watched conditions (e.g., "when emotion=frustration", "after task completion")
- Evaluate conditions against pipeline state (emotion detection output, task status)
- Compound triggers: AND/OR/SEQUENCE logic for complex conditions

#### Adaptive Monitoring (Dynamic Multiprocess Framework)

Following Scullin et al. (2013), monitoring intensity adapts dynamically:

- **Low monitoring**: No high-priority intentions match current context — minimal polling
- **Elevated monitoring**: Current topic has >0.6 cosine similarity to any pending
  high-priority intention — increase polling frequency, lower firing threshold
- **Post-trigger relaxation**: After an intention fires, return to low monitoring
  unless other relevant intentions remain active

This prevents the constant-cost problem of naive polling while ensuring
time-critical intentions are not missed.

#### Intention Extraction Pipeline

**Heuristic extraction (synchronous, ~1ms):**

Pattern matching against common prospective language:
- "remind me to...", "next time... mention/ask/check..."
- "don't forget to...", "follow up on..."
- "when we talk about X, bring up Y"
- "let me know if..."

**LLM extraction (asynchronous, 1-3s via Qwen2.5-1.5B):**

Runs in the existing async extraction pipeline alongside fact extraction:

```json
{
  "intentions": [{
    "content": "Ask about Q4 presentation results",
    "trigger_type": "time",
    "trigger_condition": "2026-02-17T09:00:00",
    "priority": 0.8
  }]
}
```

#### Context Injection — Token-Efficient Nudging

When an intention fires, it is injected as a soft nudge in the system prompt,
not as a hard instruction. Token budget: 300-500 tokens (~5% of context window).

Selection scoring (ACT-R inspired activation):

```
Score = 0.4 * base_priority
      + 0.3 * semantic_relevance_to_current_input
      + 0.2 * time_urgency (increases as deadline approaches)
      + 0.1 * freshness_decay (exponential, configurable half-life)
```

Injection format:

```
[Memory Note: You previously noted to ask about the Q4 presentation results.
This was flagged on Feb 10. Consider bringing this up naturally if relevant
to the current conversation.]
```

The model decides whether to act on the nudge based on conversational context.

#### Intention Lifecycle

```
CREATED → PENDING → TRIGGERED → EXECUTED (archived to Cold)
                  ↘ EXPIRED (TTL exceeded, archived to Cold)
                  ↘ CANCELLED (user manually cancelled)
           TRIGGERED → RECURRING (fire_count < max_fires → back to PENDING)
```

Garbage collection: intentions with effective priority below noise threshold
(0.05) after decay are automatically archived to Cold tier.

#### Solving the Circular Dependency Problem

Li & Laird (2013) identified the fundamental challenge: the system can't retrieve
an intention it doesn't know it has forgotten. The dual-pathway architecture
solves this:

- **Spontaneous retrieval** (Pathway 2) solves it for event-based PM: incoming
  inputs automatically activate matching intentions via embedding similarity,
  without the system "knowing" to look for them.
- **Strategic monitoring** (Pathway 1) solves it for time-based PM: periodic
  polling catches intentions that no environmental cue would surface.
- The hybrid approach ensures complete coverage at minimal cost.

---

## Next Steps

See the other documentation files for more information:

- **[Getting Started](getting-started.md)** - Installation and quick start guide
- **[API Reference](api-reference.md)** - Complete API documentation
