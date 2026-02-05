# ARIA Protocol Architecture

This document describes the technical architecture of the ARIA Protocol, a peer-to-peer network for distributed AI inference.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARIA PROTOCOL v0.1.0                               │
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
│  │  │  (blockchain)   │  │ (mining=infer)  │  │ (energy track)  │      │   │
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
│  │ ✓ Full protocol flow (ledger, proofs, rewards)        │   │
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

Ensures transparency, accountability, and fair rewards.

#### Provenance Ledger (`ledger.py`)

An immutable blockchain recording all inference operations:

```
┌─────────────────────────────────────────────────────────────┐
│                   Provenance Blockchain                      │
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
│  │ miner_id: "node-xyz"                              │       │
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
│  Key Property: NO model weights on-chain, only metadata      │
└─────────────────────────────────────────────────────────────┘
```

#### Proof of Useful Work (`proof.py`)

Unlike Bitcoin's wasteful hash mining, ARIA's mining IS inference:

```
┌─────────────────────────────────────────────────────────────┐
│                  Proof of Useful Work                        │
│                                                              │
│    Bitcoin                         ARIA                      │
│    ───────                         ────                      │
│    hash(nonce) → reward     inference(query) → reward        │
│    Wasted energy            Actual AI work                   │
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
│  Block Producer Selection:                                   │
│  - Track verified work count per node per epoch              │
│  - Node with most useful work becomes block producer         │
│  - More inference = higher chance of producing blocks        │
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
│    // Economics                                              │
│    min_reward_per_inference: 0.001  // Minimum ARIA tokens   │
│  }                                                           │
│                                                              │
│  Consent Matching:                                           │
│  request.matches(consent) → bool                             │
│  - Checks schedule availability                              │
│  - Verifies task type is accepted                            │
│  - Ensures resource requirements fit limits                  │
│  - Confirms reward meets minimum threshold                   │
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
│  │  Tokens: 0.042    │  │                   │               │
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
│  │ → Node eligible for block production                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│           │                                                                 │
│           ▼                                                                 │
│  7. CALCULATE REWARD                                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ reward = base_rate × quality_score × efficiency_bonus                 │  │
│  │                                                                       │  │
│  │ base_rate = 0.001 ARIA                                                │  │
│  │ quality = 1 - (latency - 1000ms) / 4000ms    [0, 1]                  │  │
│  │ efficiency = min(2.0, max(0.5, 150mJ / energy))   [0.5, 2.0]         │  │
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
│  │ (engine)  │         │(blockchain)│         │(contracts)│                 │
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
│   ├── __init__.py      # Package exports
│   ├── node.py          # ARIANode - main orchestrator
│   ├── network.py       # ARIANetwork - P2P WebSocket layer
│   ├── inference.py     # InferenceEngine, TernaryLayer, ModelShard
│   ├── bitnet_native.py     # Native ctypes bindings to bitnet.cpp
│   ├── bitnet_subprocess.py # Subprocess backend using llama-cli.exe
│   ├── ledger.py        # ProvenanceLedger, Block, InferenceRecord
│   ├── proof.py         # ProofOfUsefulWork, ProofOfSobriety
│   ├── consent.py       # ARIAConsent, TaskType
│   ├── cli.py           # Command-line interface
│   ├── api.py           # OpenAI-compatible HTTP API
│   └── dashboard.py     # Real-time web dashboard
├── tests/
│   ├── test_node.py
│   ├── test_inference.py
│   ├── test_ledger.py
│   ├── test_proof.py
│   └── test_consent.py
├── examples/
│   ├── demo.py          # Full protocol demonstration
│   └── openai_client.py # OpenAI client example
├── docs/
│   ├── architecture.md  # This document
│   ├── getting-started.md
│   └── api-reference.md
├── pyproject.toml       # Python package configuration
├── Makefile             # Build and test commands
└── README.md
```

## Next Steps

See the other documentation files for more information:

- **[Getting Started](getting-started.md)** - Installation and quick start guide
- **[API Reference](api-reference.md)** - Complete API documentation
