#!/usr/bin/env python3
"""
ARIA Protocol - Real Network Demo
Demonstrates the full ARIA protocol with real WebSocket networking:
1. Create 3 nodes with explicit consent on different ports
2. Start WebSocket servers and connect nodes via P2P
3. Load 1-bit model shards distributed across nodes
4. Process inference requests with real network communication
5. Verify provenance and energy efficiency

Run: python examples/demo.py
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.node import ARIANode
from aria.consent import ARIAConsent, TaskType


async def run_demo():
    print("=" * 60)
    print("  ARIA Protocol - Real Network Demo")
    print("  Autonomous Responsible Intelligence Architecture")
    print("=" * 60)
    print()

    # ==========================================
    # Step 1: Create nodes with explicit consent
    # ==========================================
    print("[1/7] Creating ARIA nodes with consent contracts...")
    print()

    # Node Alice: Contributes 25% CPU during work hours - Port 8765
    alice_consent = ARIAConsent(
        cpu_percent=25,
        schedule="08:00-22:00",
        task_types=[TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION],
        max_ram_mb=512,
        max_bandwidth_mbps=10,
    )
    alice = ARIANode(consent=alice_consent, port=8765, node_id="alice")

    # Node Bob: Contributes 50% CPU anytime - Port 8766
    bob_consent = ARIAConsent(
        cpu_percent=50,
        schedule="00:00-23:59",
        task_types=[TaskType.ANY],
        max_ram_mb=1024,
        max_bandwidth_mbps=50,
    )
    bob = ARIANode(consent=bob_consent, port=8766, node_id="bob")

    # Node Carol: Lightweight contributor (phone/RPi) - Port 8767
    carol_consent = ARIAConsent(
        cpu_percent=10,
        schedule="20:00-08:00",  # Overnight only
        task_types=[TaskType.TEXT_GENERATION],
        max_ram_mb=256,
        max_bandwidth_mbps=5,
    )
    carol = ARIANode(consent=carol_consent, port=8767, node_id="carol")

    print(f"  Alice (port 8765): {alice_consent}")
    print(f"  Bob   (port 8766): {bob_consent}")
    print(f"  Carol (port 8767): {carol_consent}")
    print()

    # ==========================================
    # Step 2: Load model shards
    # ==========================================
    print("[2/7] Loading 1-bit model shards (aria-2b-1bit)...")
    print()

    # Distribute model layers across nodes
    # Total: 24 layers, split into 3 shards
    shard_a = alice.load_model("aria-2b-1bit", num_layers=24, shard_start=0, shard_end=7)
    shard_b = bob.load_model("aria-2b-1bit", num_layers=24, shard_start=8, shard_end=15)
    shard_c = carol.load_model("aria-2b-1bit", num_layers=24, shard_start=16, shard_end=23)

    print(f"  Alice:  layers 0-7   ({shard_a.size_bytes:,} bytes)")
    print(f"  Bob:    layers 8-15  ({shard_b.size_bytes:,} bytes)")
    print(f"  Carol:  layers 16-23 ({shard_c.size_bytes:,} bytes)")
    print(f"  Total model memory: ~{(shard_a.size_bytes + shard_b.size_bytes + shard_c.size_bytes) / 1024 / 1024:.1f} MB")
    print()

    # ==========================================
    # Step 3: Start nodes (WebSocket servers)
    # ==========================================
    print("[3/7] Starting ARIA nodes (WebSocket servers)...")
    print()

    # Start all nodes concurrently
    await asyncio.gather(
        alice.start(),
        bob.start(),
        carol.start(),
    )

    # Small delay to ensure servers are ready
    await asyncio.sleep(0.5)
    print()

    # ==========================================
    # Step 4: Connect nodes (P2P mesh)
    # ==========================================
    print("[4/7] Connecting nodes via WebSocket (P2P mesh)...")
    print()

    # Each node connects to the other nodes
    # This creates a mesh topology where everyone knows everyone
    seed_peers = ["localhost:8765", "localhost:8766", "localhost:8767"]

    await asyncio.gather(
        alice.connect_to_peers(seed_peers),
        bob.connect_to_peers(seed_peers),
        carol.connect_to_peers(seed_peers),
    )

    # Small delay for connections to stabilize
    await asyncio.sleep(0.5)

    # Show connection status
    for node in [alice, bob, carol]:
        stats = node.network.get_network_stats()
        print(f"  {node.node_id}: {stats['connected_peers']} connected peers, "
              f"{stats['alive_peers']} known peers")
    print()

    # ==========================================
    # Step 5: Process inference requests
    # ==========================================
    print("[5/7] Processing inference requests...")
    print()

    queries = [
        "What is the meaning of life?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about artificial intelligence.",
        "How does blockchain work?",
        "What are the benefits of renewable energy?",
        "Describe the architecture of a neural network.",
        "What is the future of decentralized AI?",
        "Explain the concept of proof of work.",
        "How can P2P networks improve AI efficiency?",
        "What role does consent play in ethical AI?",
    ]

    nodes = [alice, bob, carol]

    for i, query in enumerate(queries):
        # Round-robin across nodes
        node = nodes[i % 3]
        result = node.process_request(query)
        print(f"  Query {i+1}: \"{query[:45]}...\"")
        print(f"    Node: {node.node_id} | Latency: {result.latency_ms}ms | "
              f"Energy: {result.energy_mj:.2f}mJ | Tokens: {result.tokens_generated}")

    print()

    # ==========================================
    # Step 6: Demonstrate P2P inference request
    # ==========================================
    print("[6/7] Testing P2P inference request (Alice -> Bob)...")
    print()

    # Alice sends an inference request to Bob over the network
    response = await alice.send_inference_request(
        peer_id="bob",
        query="What is distributed computing?",
        max_tokens=50
    )

    if response and response.get("status") == "completed":
        result = response.get("result", {})
        print(f"  Request sent from Alice to Bob")
        print(f"  Response: {result.get('tokens', 'N/A')} tokens, "
              f"latency: {result.get('latency_ms', 'N/A')}ms")
    else:
        print(f"  P2P request completed (response: {response})")
    print()

    # ==========================================
    # Step 7: Verify provenance and stop
    # ==========================================
    print("[7/7] Verifying provenance ledger and stopping nodes...")
    print()

    # Force mine remaining records
    for node in nodes:
        if node.ledger.pending_records:
            node.ledger.mine_pending_block(miner_id=node.node_id)

    for node in nodes:
        stats = node.ledger.get_network_stats()
        print(f"  {node.node_id}: {stats['total_inferences']} inferences recorded, "
              f"chain valid: {stats['chain_valid']}")

    print()

    # Stop nodes (triggers sobriety attestation)
    await asyncio.gather(
        alice.stop(),
        bob.stop(),
        carol.stop(),
    )
    print()

    # ==========================================
    # Final Summary
    # ==========================================
    total_inferences = sum(n.engine.total_inferences for n in nodes)
    total_energy = sum(n.engine.total_energy_mj for n in nodes)
    total_tokens = sum(n.tokens_earned for n in nodes)
    total_messages = sum(n.network.messages_sent + n.network.messages_received for n in nodes)

    gpu_equivalent = total_inferences * 150  # 150 mJ per inference on GPU
    savings = gpu_equivalent - total_energy

    print("=" * 60)
    print("  ARIA Network Summary")
    print("=" * 60)
    print(f"  Nodes active:           3")
    print(f"  Total inferences:       {total_inferences}")
    print(f"  Network messages:       {total_messages}")
    print(f"  Total energy (ARIA):    {total_energy:.1f} mJ")
    print(f"  GPU equivalent:         {gpu_equivalent:.1f} mJ")
    print(f"  Energy saved:           {savings:.1f} mJ ({savings/max(gpu_equivalent,1)*100:.1f}%)")
    print(f"  Tokens earned (total):  {total_tokens:.6f} ARIA")
    print(f"  Ledger integrity:       {'VALID' if alice.ledger.verify_chain() else 'INVALID'}")
    print()
    print("  Real WebSocket P2P:     Nodes communicate over localhost")
    print("  Proof of Useful Work:   Mining IS inference.")
    print("  Proof of Sobriety:      Every joule is accounted for.")
    print("  Consent:                Every node chose to be here.")
    print()
    print("  ARIA Protocol v0.1.0 - MIT License")
    print("=" * 60)


def main():
    """Entry point for the demo."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n[ARIA] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ARIA] Error: {e}")
        raise


if __name__ == "__main__":
    main()
