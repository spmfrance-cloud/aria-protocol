#!/usr/bin/env python3
"""
ARIA Protocol - Demo
Demonstrates the full ARIA protocol cycle:
1. Create nodes with explicit consent
2. Load 1-bit model shards
3. Process inference requests
4. Record provenance on the ledger
5. Verify Proof of Useful Work
6. Measure energy efficiency (Proof of Sobriety)

Run: python examples/demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.node import ARIANode
from aria.consent import ARIAConsent, TaskType

def main():
    print("=" * 60)
    print("  ARIA Protocol - Reference Implementation Demo")
    print("  Autonomous Responsible Intelligence Architecture")
    print("=" * 60)
    print()
    
    # ==========================================
    # Step 1: Create nodes with explicit consent
    # ==========================================
    print("[1/6] Creating ARIA nodes with consent contracts...")
    print()
    
    # Node Alice: Contributes 25% CPU during work hours
    alice_consent = ARIAConsent(
        cpu_percent=25,
        schedule="08:00-22:00",
        task_types=[TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION],
        max_ram_mb=512,
        max_bandwidth_mbps=10,
    )
    alice = ARIANode(consent=alice_consent, port=8765, node_id="alice")
    
    # Node Bob: Contributes 50% CPU anytime 
    bob_consent = ARIAConsent(
        cpu_percent=50,
        schedule="00:00-23:59",
        task_types=[TaskType.ANY],
        max_ram_mb=1024,
        max_bandwidth_mbps=50,
    )
    bob = ARIANode(consent=bob_consent, port=8766, node_id="bob")
    
    # Node Carol: Lightweight contributor (phone/RPi)
    carol_consent = ARIAConsent(
        cpu_percent=10,
        schedule="20:00-08:00",  # Overnight only
        task_types=[TaskType.TEXT_GENERATION],
        max_ram_mb=256,
        max_bandwidth_mbps=5,
    )
    carol = ARIANode(consent=carol_consent, port=8767, node_id="carol")
    
    print(f"  Alice: {alice_consent}")
    print(f"  Bob:   {bob_consent}")
    print(f"  Carol: {carol_consent}")
    print()
    
    # ==========================================
    # Step 2: Load model shards
    # ==========================================
    print("[2/6] Loading 1-bit model shards (aria-2b-1bit)...")
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
    # Step 3: Start nodes
    # ==========================================
    print("[3/6] Starting ARIA nodes...")
    print()
    alice.start()
    bob.start()
    carol.start()
    print()
    
    # ==========================================
    # Step 4: Process inference requests
    # ==========================================
    print("[4/6] Processing inference requests...")
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
    
    for i, query in enumerate(queries):
        # Round-robin across nodes
        node = [alice, bob, carol][i % 3]
        result = node.process_request(query)
        print(f"  Query {i+1}: \"{query[:50]}...\"")
        print(f"    Node: {node.node_id} | Latency: {result.latency_ms}ms | "
              f"Energy: {result.energy_mj}mJ | Tokens: {result.tokens_generated}")
    
    print()
    
    # ==========================================
    # Step 5: Verify provenance ledger
    # ==========================================
    print("[5/6] Verifying provenance ledger...")
    print()
    
    # Force mine remaining records
    for node in [alice, bob, carol]:
        node.ledger.mine_pending_block(miner_id=node.node_id)
    
    for node in [alice, bob, carol]:
        stats = node.ledger.get_network_stats()
        print(f"  {node.node_id}: {stats['total_inferences']} inferences recorded, "
              f"chain valid: {stats['chain_valid']}")
    
    print()
    
    # ==========================================
    # Step 6: Energy efficiency report
    # ==========================================
    print("[6/6] Energy efficiency report (Proof of Sobriety)...")
    print()
    
    # Stop nodes (triggers sobriety attestation)
    alice.stop()
    bob.stop()
    carol.stop()
    print()
    
    # Aggregate stats
    total_inferences = sum(n.engine.total_inferences for n in [alice, bob, carol])
    total_energy = sum(n.engine.total_energy_mj for n in [alice, bob, carol])
    total_tokens = sum(n.tokens_earned for n in [alice, bob, carol])
    
    gpu_equivalent = total_inferences * 150  # 150 mJ per inference on GPU
    savings = gpu_equivalent - total_energy
    
    print("=" * 60)
    print("  ARIA Network Summary")
    print("=" * 60)
    print(f"  Nodes active:           3")
    print(f"  Total inferences:       {total_inferences}")
    print(f"  Total energy (ARIA):    {total_energy:.1f} mJ")
    print(f"  GPU equivalent:         {gpu_equivalent:.1f} mJ")
    print(f"  Energy saved:           {savings:.1f} mJ ({savings/max(gpu_equivalent,1)*100:.1f}%)")
    print(f"  Tokens earned (total):  {total_tokens:.6f} ARIA")
    print(f"  Ledger integrity:       {'VALID' if alice.ledger.verify_chain() else 'INVALID'}")
    print()
    print("  Proof of Useful Work:   Mining IS inference.")
    print("  Proof of Sobriety:      Every joule is accounted for.")
    print("  Consent:                Every node chose to be here.")
    print()
    print("  ARIA Protocol v0.1.0 - MIT License")
    print("  https://github.com/[your-repo]/aria-protocol")
    print("=" * 60)


if __name__ == "__main__":
    main()
