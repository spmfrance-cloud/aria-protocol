"""
ARIA Protocol - Distributed 1-Bit Inference Engine
Handles model sharding, distributed inference pipeline,
and result aggregation across the P2P network.

Supports real distributed pipeline parallelism:
- Each node processes its local layers
- Activations are serialized and forwarded to next node in chain
- Final node returns result to originator

MIT License - Anthony MURGO, 2026
"""

import hashlib
import time
import struct
import math
import base64
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from aria.ledger import InferenceRecord


def serialize_activations(activations: List[float]) -> str:
    """
    Serialize activations to a base64-encoded JSON string.

    Uses struct packing for efficient float representation,
    then base64 encoding for network transport.

    Args:
        activations: List of float activation values

    Returns:
        Base64-encoded string of packed floats
    """
    packed = struct.pack(f'{len(activations)}f', *activations)
    return base64.b64encode(packed).decode('ascii')


def deserialize_activations(encoded: str) -> List[float]:
    """
    Deserialize activations from a base64-encoded string.

    Args:
        encoded: Base64-encoded string of packed floats

    Returns:
        List of float activation values
    """
    packed = base64.b64decode(encoded.encode('ascii'))
    num_floats = len(packed) // 4  # 4 bytes per float
    return list(struct.unpack(f'{num_floats}f', packed))


@dataclass
class PipelineStage:
    """
    Represents a stage in the distributed inference pipeline.

    Each stage is a node that processes a specific range of layers.
    The pipeline chains stages together: stage1 -> stage2 -> stage3
    """
    node_id: str
    shard_id: str
    layer_start: int
    layer_end: int
    host: str = "localhost"
    port: int = 8765
    is_replica: bool = False  # True if this is a fallback replica

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "shard_id": self.shard_id,
            "layer_start": self.layer_start,
            "layer_end": self.layer_end,
            "host": self.host,
            "port": self.port,
            "is_replica": self.is_replica,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineStage":
        return cls(
            node_id=data["node_id"],
            shard_id=data["shard_id"],
            layer_start=data["layer_start"],
            layer_end=data["layer_end"],
            host=data.get("host", "localhost"),
            port=data.get("port", 8765),
            is_replica=data.get("is_replica", False),
        )


@dataclass
class PipelineState:
    """
    State passed through the distributed inference pipeline.

    Contains all information needed to continue inference
    from any point in the pipeline.
    """
    request_id: str
    model_id: str
    query: str
    max_tokens: int
    activations: List[float]  # Current activation state
    current_layer: int  # Next layer to process
    total_layers: int  # Total layers in model
    nodes_used: List[str] = field(default_factory=list)
    total_energy_mj: float = 0.0
    start_time: float = field(default_factory=time.time)
    originator_id: str = ""  # Node that started the request

    def to_dict(self) -> dict:
        """Serialize state for network transmission."""
        return {
            "request_id": self.request_id,
            "model_id": self.model_id,
            "query": self.query,
            "max_tokens": self.max_tokens,
            "activations_b64": serialize_activations(self.activations),
            "current_layer": self.current_layer,
            "total_layers": self.total_layers,
            "nodes_used": self.nodes_used,
            "total_energy_mj": self.total_energy_mj,
            "start_time": self.start_time,
            "originator_id": self.originator_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineState":
        """Deserialize state from network transmission."""
        return cls(
            request_id=data["request_id"],
            model_id=data["model_id"],
            query=data["query"],
            max_tokens=data["max_tokens"],
            activations=deserialize_activations(data["activations_b64"]),
            current_layer=data["current_layer"],
            total_layers=data["total_layers"],
            nodes_used=data.get("nodes_used", []),
            total_energy_mj=data.get("total_energy_mj", 0.0),
            start_time=data.get("start_time", time.time()),
            originator_id=data.get("originator_id", ""),
        )

    @property
    def is_complete(self) -> bool:
        """Check if all layers have been processed."""
        return self.current_layer >= self.total_layers


@dataclass
class ModelShard:
    """
    A shard (fragment) of a 1-bit model.

    In ARIA, large models are split into shards that can be
    distributed across multiple nodes. Each shard contains
    a contiguous set of transformer layers.
    """
    shard_id: str           # Unique identifier
    model_id: str           # Parent model identifier
    layer_start: int        # First layer in this shard
    layer_end: int          # Last layer in this shard
    size_bytes: int         # Size in bytes
    checksum: str           # SHA-256 of shard data
    weights: Optional[bytes] = None  # Actual ternary weights

    @property
    def num_layers(self) -> int:
        return self.layer_end - self.layer_start + 1


@dataclass
class InferenceResult:
    """Result of a distributed inference."""
    request_id: str
    output_tokens: List[int]    # Generated token IDs
    output_text: str            # Decoded text
    latency_ms: int             # Total inference time
    energy_mj: int              # Energy consumed (millijoules)
    nodes_used: List[str]       # Node IDs that contributed
    model_id: str               # Model used
    tokens_generated: int       # Count of output tokens
    
    def to_provenance_record(self, query: str) -> InferenceRecord:
        """Convert to a provenance record for the ledger."""
        return InferenceRecord(
            query_hash=hashlib.sha256(query.encode()).hexdigest(),
            output_hash=hashlib.sha256(self.output_text.encode()).hexdigest(),
            model_id=self.model_id,
            node_ids=self.nodes_used,
            energy_mj=self.energy_mj,
            latency_ms=self.latency_ms,
            timestamp=time.time(),
            tokens_generated=self.tokens_generated,
        )


class TernaryLayer:
    """
    A simulated 1-bit (ternary) transformer layer.
    
    In production, this would interface with bitnet.cpp or
    a similar optimized 1-bit inference engine. This reference
    implementation simulates the computation to demonstrate
    the protocol mechanics.
    
    Ternary weights: each weight is -1, 0, or +1
    This means:
    - No floating-point multiplication needed
    - Matrix-vector product = additions and subtractions only
    - Massive memory savings: ~10x less than FP16
    """
    
    def __init__(self, input_dim: int, output_dim: int, layer_id: int):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.layer_id = layer_id
        
        # Simulate ternary weights as packed bytes
        # In real implementation: actual trained ternary weights
        self.weight_count = input_dim * output_dim
        self.memory_bytes = math.ceil(self.weight_count * 1.58 / 8)  # 1.58 bits per weight
    
    def forward(self, activations: List[float]) -> List[float]:
        """
        Forward pass through this ternary layer.
        
        In production: bitnet.cpp kernel with AVX2/NEON
        Here: simulation that demonstrates the computation model
        
        The key insight: instead of y = W @ x (matrix multiply),
        we compute y = sum of x[j] where W[i][j] == 1
                     - sum of x[j] where W[i][j] == -1
        
        This is pure addition/subtraction. No multiplication.
        """
        # Simulate output (deterministic based on input hash)
        input_hash = hashlib.sha256(
            struct.pack(f'{len(activations)}f', *activations)
        ).digest()
        
        output = []
        for i in range(self.output_dim):
            # Deterministic pseudo-random value based on input + layer
            seed = int.from_bytes(input_hash[i % 16:(i % 16) + 4], 'big')
            value = ((seed % 1000) / 1000.0) * 2 - 1  # [-1, 1]
            output.append(value)
        
        return output
    
    def energy_estimate_mj(self) -> float:
        """
        Estimate energy consumption for one forward pass.
        
        Based on BitNet benchmarks:
        - ~0.028 J per inference for a 2B parameter model
        - Scales linearly with layer count
        """
        # ~0.001 mJ per 1000 ternary operations on CPU
        ops = self.weight_count
        return ops * 0.000001  # millijoules


class InferenceEngine:
    """
    The ARIA distributed inference engine.
    
    Manages model shards, executes inference pipelines,
    and coordinates distributed computation across nodes.
    
    Usage:
        engine = InferenceEngine(node_id="my_node")
        engine.load_model("aria-2b-1bit", num_layers=24)
        
        result = engine.infer(
            query="What is the meaning of life?",
            max_tokens=100
        )
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.loaded_shards: Dict[str, ModelShard] = {}
        self.layers: Dict[str, List[TernaryLayer]] = {}  # model_id -> layers
        self.total_inferences = 0
        self.total_energy_mj = 0.0
    
    def load_model(self, model_id: str, num_layers: int = 24, 
                   hidden_dim: int = 2048, shard_start: int = 0,
                   shard_end: Optional[int] = None):
        """
        Load model layers for local inference.
        
        In a distributed setup, each node loads only a subset
        of layers (its shard). The full model is reconstructed
        through pipeline parallelism across nodes.
        
        Args:
            model_id: Model identifier
            num_layers: Total layers in the model
            hidden_dim: Hidden dimension size
            shard_start: First layer to load on this node
            shard_end: Last layer to load (None = all remaining)
        """
        if shard_end is None:
            shard_end = num_layers - 1
        
        layers = []
        for i in range(shard_start, shard_end + 1):
            layer = TernaryLayer(hidden_dim, hidden_dim, i)
            layers.append(layer)
        
        self.layers[model_id] = layers
        
        # Create shard descriptor
        shard = ModelShard(
            shard_id=f"{model_id}_L{shard_start}-{shard_end}",
            model_id=model_id,
            layer_start=shard_start,
            layer_end=shard_end,
            size_bytes=sum(l.memory_bytes for l in layers),
            checksum=hashlib.sha256(model_id.encode()).hexdigest()[:16],
        )
        self.loaded_shards[shard.shard_id] = shard
        
        return shard
    
    def get_loaded_shard_ids(self) -> List[str]:
        """Get IDs of all loaded shards."""
        return list(self.loaded_shards.keys())
    
    def infer(self, query: str, model_id: str = "aria-2b-1bit",
              max_tokens: int = 100) -> InferenceResult:
        """
        Run inference on the local model shard.
        
        In a full ARIA network, this would be one step in a
        distributed pipeline. The orchestrator chains multiple
        nodes together to process all layers sequentially.
        
        Args:
            query: Input text
            model_id: Which model to use
            max_tokens: Maximum output tokens
            
        Returns:
            InferenceResult with output, timing, and energy data
        """
        start_time = time.time()
        
        layers = self.layers.get(model_id, [])
        if not layers:
            raise ValueError(f"Model {model_id} not loaded on this node")
        
        # Tokenize (simplified)
        input_tokens = self._tokenize(query)
        
        # Initial activations from token embeddings
        activations = [float(t) / 1000.0 for t in input_tokens]
        # Pad/truncate to hidden_dim
        hidden_dim = layers[0].input_dim
        activations = (activations + [0.0] * hidden_dim)[:hidden_dim]
        
        # Forward pass through all local layers
        total_energy = 0.0
        for layer in layers:
            activations = layer.forward(activations)
            total_energy += layer.energy_estimate_mj()
        
        # Generate output tokens (simplified)
        output_tokens = self._generate_tokens(activations, max_tokens)
        output_text = self._detokenize(output_tokens)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        self.total_inferences += 1
        self.total_energy_mj += total_energy
        
        return InferenceResult(
            request_id=hashlib.sha256(f"{query}{time.time()}".encode()).hexdigest()[:16],
            output_tokens=output_tokens,
            output_text=output_text,
            latency_ms=elapsed_ms,
            energy_mj=int(total_energy),
            nodes_used=[self.node_id],
            model_id=model_id,
            tokens_generated=len(output_tokens),
        )
    
    def _tokenize(self, text: str) -> List[int]:
        """Simple tokenizer (placeholder for real BPE tokenizer)."""
        return [ord(c) for c in text[:512]]
    
    def _generate_tokens(self, activations: List[float], max_tokens: int) -> List[int]:
        """Generate output tokens from final activations."""
        tokens = []
        for i in range(min(max_tokens, len(activations))):
            # Map activation to token ID (simplified)
            token_id = int(abs(activations[i]) * 50000) % 50000
            tokens.append(token_id)
        return tokens
    
    def _detokenize(self, tokens: List[int]) -> str:
        """Convert token IDs back to text (placeholder)."""
        # In production: proper BPE detokenization
        return f"[ARIA inference output: {len(tokens)} tokens generated]"

    def create_pipeline_state(self, query: str, model_id: str = "aria-2b-1bit",
                              max_tokens: int = 100, total_layers: int = 24,
                              originator_id: str = "") -> PipelineState:
        """
        Create initial pipeline state for distributed inference.

        This tokenizes the query and creates the initial activations
        that will be passed through the distributed pipeline.

        Args:
            query: Input text
            model_id: Which model to use
            max_tokens: Maximum output tokens
            total_layers: Total layers in the full model
            originator_id: Node that started the request

        Returns:
            PipelineState ready to be processed by first node in chain
        """
        # Tokenize and create initial activations
        input_tokens = self._tokenize(query)
        hidden_dim = 2048  # Default hidden dimension

        # Initial activations from token embeddings
        activations = [float(t) / 1000.0 for t in input_tokens]
        activations = (activations + [0.0] * hidden_dim)[:hidden_dim]

        return PipelineState(
            request_id=hashlib.sha256(f"{query}{time.time()}".encode()).hexdigest()[:16],
            model_id=model_id,
            query=query,
            max_tokens=max_tokens,
            activations=activations,
            current_layer=0,
            total_layers=total_layers,
            nodes_used=[],
            total_energy_mj=0.0,
            originator_id=originator_id or self.node_id,
        )

    def process_pipeline_stage(self, state: PipelineState) -> Tuple[PipelineState, Optional[InferenceResult]]:
        """
        Process the pipeline state through local layers.

        This is the core of distributed inference:
        1. Takes activations from previous node
        2. Processes through all local layers
        3. Returns updated state (or final result if complete)

        Args:
            state: Current pipeline state with activations

        Returns:
            Tuple of (updated_state, result)
            - If not complete: (new_state, None) - forward to next node
            - If complete: (final_state, InferenceResult) - return to originator
        """
        model_id = state.model_id
        layers = self.layers.get(model_id, [])

        if not layers:
            raise ValueError(f"Model {model_id} not loaded on this node")

        # Get our shard info
        shard = None
        for s in self.loaded_shards.values():
            if s.model_id == model_id:
                shard = s
                break

        if not shard:
            raise ValueError(f"No shard loaded for model {model_id}")

        # Check if this stage should process
        if state.current_layer > shard.layer_end:
            # We've already processed past this shard, pass through
            return state, None

        if state.current_layer < shard.layer_start:
            # State is asking for earlier layers we don't have
            raise ValueError(
                f"Pipeline state at layer {state.current_layer} but "
                f"this node has layers {shard.layer_start}-{shard.layer_end}"
            )

        # Process through our local layers
        activations = state.activations
        total_energy = 0.0

        # Only process layers within our shard that are at or after current_layer
        for layer in layers:
            if layer.layer_id < state.current_layer:
                continue
            if layer.layer_id > shard.layer_end:
                break

            activations = layer.forward(activations)
            total_energy += layer.energy_estimate_mj()

        # Update state
        new_state = PipelineState(
            request_id=state.request_id,
            model_id=state.model_id,
            query=state.query,
            max_tokens=state.max_tokens,
            activations=activations,
            current_layer=shard.layer_end + 1,  # Next layer to process
            total_layers=state.total_layers,
            nodes_used=state.nodes_used + [self.node_id],
            total_energy_mj=state.total_energy_mj + total_energy,
            start_time=state.start_time,
            originator_id=state.originator_id,
        )

        self.total_inferences += 1
        self.total_energy_mj += total_energy

        # Check if we're the final stage
        if new_state.is_complete:
            # Generate final output
            output_tokens = self._generate_tokens(activations, state.max_tokens)
            output_text = self._detokenize(output_tokens)

            elapsed_ms = int((time.time() - state.start_time) * 1000)

            result = InferenceResult(
                request_id=state.request_id,
                output_tokens=output_tokens,
                output_text=output_text,
                latency_ms=elapsed_ms,
                energy_mj=int(new_state.total_energy_mj),
                nodes_used=new_state.nodes_used,
                model_id=state.model_id,
                tokens_generated=len(output_tokens),
            )

            return new_state, result

        # Not complete, needs to be forwarded
        return new_state, None

    def get_shard_info(self, model_id: str) -> Optional[ModelShard]:
        """Get the shard loaded for a specific model."""
        for shard in self.loaded_shards.values():
            if shard.model_id == model_id:
                return shard
        return None

    def get_stats(self) -> Dict:
        """Get inference engine statistics."""
        return {
            "node_id": self.node_id,
            "loaded_models": list(self.layers.keys()),
            "loaded_shards": len(self.loaded_shards),
            "total_layers": sum(len(l) for l in self.layers.values()),
            "total_memory_bytes": sum(s.size_bytes for s in self.loaded_shards.values()),
            "total_inferences": self.total_inferences,
            "total_energy_mj": self.total_energy_mj,
            "avg_energy_per_inference_mj": (
                self.total_energy_mj / self.total_inferences 
                if self.total_inferences > 0 else 0
            ),
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"InferenceEngine(node={self.node_id}, "
            f"models={stats['loaded_models']}, "
            f"layers={stats['total_layers']}, "
            f"inferences={stats['total_inferences']})"
        )
