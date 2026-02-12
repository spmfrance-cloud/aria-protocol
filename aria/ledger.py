"""
ARIA Protocol - Provenance Ledger
A lightweight provenance ledger for tracking AI inference history.
Every inference is recorded immutably with full traceability.

MIT License - Anthony MURGO, 2026
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict


@dataclass
class InferenceRecord:
    """
    An immutable record of a single AI inference.
    This is the atomic unit of ARIA's provenance system.
    
    Every AI output can be traced back to:
    - What was asked (query_hash)
    - What model produced it (model_id)
    - Which nodes computed it (node_ids)  
    - How much energy it consumed (energy_mj)
    - When it happened (timestamp)
    """
    query_hash: str          # SHA-256 of the input query
    output_hash: str         # SHA-256 of the output
    model_id: str            # Identifier of the model used
    node_ids: List[str]      # Nodes that contributed to this inference
    energy_mj: int           # Energy consumed in millijoules
    latency_ms: int          # Total latency in milliseconds
    timestamp: float         # Unix timestamp
    tokens_generated: int    # Number of output tokens
    
    def to_hash(self) -> str:
        """Generate unique record identifier."""
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class Block:
    """
    A block in the ARIA provenance chain.
    Contains multiple inference records and links to the previous block.
    """
    index: int
    timestamp: float
    records: List[InferenceRecord]
    previous_hash: str
    nonce: int = 0
    contributor_id: str = ""
    
    # Computed
    hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute block hash from all contents."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "records": [asdict(r) for r in self.records],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "contributor_id": self.contributor_id,
        }
        data = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def seal(self, difficulty: int = 2) -> str:
        """
        Seal this block with Proof of Useful Work.

        In ARIA, every computation is useful inference. The nonce is the count of
        useful inferences performed. The difficulty adjusts to
        maintain a target block time.

        For the reference implementation, we use a simple
        hash-based proof with leading zeros.
        """
        prefix = "0" * difficulty
        while True:
            self.hash = self.compute_hash()
            if self.hash.startswith(prefix):
                return self.hash
            self.nonce += 1


class ProvenanceLedger:
    """
    The ARIA provenance ledger.

    A lightweight chain optimized for AI inference metadata.
    Stores only hashes and provenance data — no model weights
    or actual inference data on-chain.
    
    Usage:
        ledger = ProvenanceLedger()
        
        record = InferenceRecord(
            query_hash=sha256("Hello, how are you?"),
            output_hash=sha256("I'm doing well, thanks!"),
            model_id="aria-2b-1bit-v1",
            node_ids=["node_abc", "node_def"],
            energy_mj=28,
            latency_ms=450,
            timestamp=time.time(),
            tokens_generated=12
        )
        
        ledger.add_record(record)
    """
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_records: List[InferenceRecord] = []
        self.difficulty = difficulty
        self.records_per_block = 10  # Max records per block
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain."""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            records=[],
            previous_hash="0" * 64,
            contributor_id="genesis",
        )
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)
    
    @property
    def last_block(self) -> Block:
        """Get the most recent block."""
        return self.chain[-1]
    
    def add_record(self, record: InferenceRecord) -> str:
        """
        Add an inference record to the pending pool.
        Returns the record hash for reference.
        
        When enough records accumulate, a new block is sealed.
        """
        record_hash = record.to_hash()
        self.pending_records.append(record)
        
        # Auto-seal when we have enough records
        if len(self.pending_records) >= self.records_per_block:
            self.seal_pending_block()
        
        return record_hash
    
    def seal_pending_block(self, contributor_id: str = "local") -> Optional[Block]:
        """Seal a new block with all pending records."""
        if not self.pending_records:
            return None
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            records=self.pending_records[:self.records_per_block],
            previous_hash=self.last_block.hash,
            contributor_id=contributor_id,
        )

        new_block.seal(self.difficulty)
        self.chain.append(new_block)
        self.pending_records = self.pending_records[self.records_per_block:]
        
        return new_block
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire chain.
        Returns True if no tampering is detected.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Verify hash
            if current.hash != current.compute_hash():
                return False
            
            # Verify chain linkage
            if current.previous_hash != previous.hash:
                return False
        
        return True
    
    def get_record_by_hash(self, record_hash: str) -> Optional[InferenceRecord]:
        """Look up a specific inference record by its hash."""
        for block in self.chain:
            for record in block.records:
                if record.to_hash() == record_hash:
                    return record
        return None
    
    def get_records_by_node(self, node_id: str) -> List[InferenceRecord]:
        """Get all inference records involving a specific node."""
        results = []
        for block in self.chain:
            for record in block.records:
                if node_id in record.node_ids:
                    results.append(record)
        return results
    
    def get_records_by_model(self, model_id: str) -> List[InferenceRecord]:
        """Get all inference records for a specific model."""
        results = []
        for block in self.chain:
            for record in block.records:
                if record.model_id == model_id:
                    results.append(record)
        return results
    
    def get_network_stats(self) -> Dict:
        """Compute aggregate statistics for the network."""
        total_inferences = 0
        total_energy_mj = 0
        total_tokens = 0
        total_latency_ms = 0
        unique_nodes = set()
        unique_models = set()
        
        for block in self.chain:
            for record in block.records:
                total_inferences += 1
                total_energy_mj += record.energy_mj
                total_tokens += record.tokens_generated
                total_latency_ms += record.latency_ms
                unique_nodes.update(record.node_ids)
                unique_models.add(record.model_id)
        
        return {
            "total_inferences": total_inferences,
            "total_energy_joules": total_energy_mj / 1000,
            "total_tokens_generated": total_tokens,
            "avg_latency_ms": total_latency_ms / max(total_inferences, 1),
            "avg_energy_per_inference_mj": total_energy_mj / max(total_inferences, 1),
            "unique_nodes": len(unique_nodes),
            "unique_models": len(unique_models),
            "chain_length": len(self.chain),
            "chain_valid": self.verify_chain(),
        }
    
    def export_chain(self) -> str:
        """Export the full chain as JSON."""
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
                "contributor_id": block.contributor_id,
                "records": [asdict(r) for r in block.records],
            })
        return json.dumps(chain_data, indent=2)
    
    def __repr__(self) -> str:
        stats = self.get_network_stats()
        return (
            f"ProvenanceLedger(blocks={stats['chain_length']}, "
            f"inferences={stats['total_inferences']}, "
            f"nodes={stats['unique_nodes']}, "
            f"valid={stats['chain_valid']})"
        )
