"""
ARIA Protocol - Core Node
The main ARIA node that ties everything together.
Join the network. Contribute compute. Earn rewards.

MIT License - Anthony MURGO, 2026
"""

import asyncio
import hashlib
import json
import time
import uuid
from typing import Optional, Dict, List

from aria.consent import ARIAConsent, TaskType
from aria.network import ARIANetwork, PeerInfo, InferenceRequest
from aria.inference import InferenceEngine, InferenceResult, PipelineState
from aria.ledger import ProvenanceLedger, InferenceRecord
from aria.proof import ProofOfUsefulWork, ProofOfSobriety


class ARIANode:
    """
    A node in the ARIA network.

    This is the primary entry point for participating in ARIA.
    A node can contribute CPU resources for AI inference and
    earn ARIA tokens in return.

    Minimal example (async):
        node = ARIANode(cpu_percent=25, port=8765)
        await node.start()
        await node.connect_to_peers(["localhost:8766"])

    Full example:
        consent = ARIAConsent(
            cpu_percent=25,
            schedule="08:00-22:00",
            task_types=[TaskType.TEXT_GENERATION],
            max_bandwidth_mbps=10,
            max_ram_mb=512
        )

        node = ARIANode(consent=consent, port=8765)
        node.load_model("aria-2b-1bit")
        await node.start()
        await node.connect_to_peers(["localhost:8766", "localhost:8767"])

        # Process a request
        result = node.process_request("What is AI?")
        print(result.output_text)
        print(node.get_stats())

        await node.stop()
    """

    def __init__(self,
                 consent: Optional[ARIAConsent] = None,
                 cpu_percent: int = 25,
                 port: int = 8765,
                 node_id: Optional[str] = None):
        """
        Initialize an ARIA node.

        Args:
            consent: Explicit consent descriptor. If None, creates default.
            cpu_percent: CPU percentage to allocate (used if consent is None)
            port: Network port for P2P communication
            node_id: Unique node identifier. Auto-generated if None.
        """
        # Generate unique node ID
        self.node_id = node_id or f"aria_{uuid.uuid4().hex[:12]}"

        # Consent
        self.consent = consent or ARIAConsent(cpu_percent=cpu_percent)
        self.consent.node_id = self.node_id

        # Core components
        self.network = ARIANetwork(
            node_id=self.node_id,
            port=port,
            consent=self.consent
        )
        self.engine = InferenceEngine(node_id=self.node_id)
        self.ledger = ProvenanceLedger(difficulty=2)
        self.pouw = ProofOfUsefulWork()
        self.sobriety = ProofOfSobriety(node_id=self.node_id)

        # State
        self.is_running = False
        self.tokens_earned = 0.0
        self.start_time: Optional[float] = None

        # Set inference callback for network requests
        self.network.set_inference_callback(self._handle_network_inference)

        # Set pipeline callback for distributed inference
        self.network.set_pipeline_callback(self._handle_pipeline_forward)

        # Set CLI command callbacks
        self.network.set_stats_callback(self.get_stats)
        self.network.set_ledger_stats_callback(self._get_ledger_stats)
        self.network.set_ledger_verify_callback(self._verify_ledger)

    def load_model(self, model_id: str = "aria-2b-1bit",
                   num_layers: int = 24, hidden_dim: int = 2048,
                   shard_start: int = 0, shard_end: Optional[int] = None):
        """
        Load a model (or model shard) for inference.

        Args:
            model_id: Model identifier
            num_layers: Total layers in the model
            hidden_dim: Hidden dimension size
            shard_start: First layer this node handles
            shard_end: Last layer this node handles
        """
        shard = self.engine.load_model(
            model_id=model_id,
            num_layers=num_layers,
            hidden_dim=hidden_dim,
            shard_start=shard_start,
            shard_end=shard_end,
        )

        # Update local shards list
        self.network.local_shards = self.engine.get_loaded_shard_ids()

        # Add ourselves to the network routing table
        self.network.add_peer(PeerInfo(
            node_id=self.node_id,
            host="localhost",
            port=self.network.port,
            consent=self.consent,
            available_shards=self.network.local_shards,
        ))

        return shard

    async def start(self):
        """
        Start the ARIA node (async).

        This begins:
        1. Starting the WebSocket server for P2P connections
        2. Listening for incoming peer connections
        3. Accepting inference requests per consent
        4. Recording provenance for all work done
        5. Measuring energy for Proof of Sobriety
        """
        if self.is_running:
            return

        self.is_running = True
        self.start_time = time.time()
        self.sobriety.start_measurement()

        # Start the network layer
        await self.network.start()

        print(f"[ARIA] Node {self.node_id} started")
        print(f"[ARIA] Consent: {self.consent}")
        print(f"[ARIA] Models: {list(self.engine.layers.keys())}")
        print(f"[ARIA] Listening on port {self.network.port}")

    async def stop(self):
        """Stop the ARIA node gracefully (async)."""
        if not self.is_running:
            return

        self.is_running = False

        # Stop network layer
        await self.network.stop()

        # Generate final sobriety attestation
        if self.engine.total_inferences > 0:
            attestation = self.sobriety.end_measurement(
                inferences_done=self.engine.total_inferences
            )
            print(f"[ARIA] Sobriety rating: {attestation.efficiency_rating}")

        # Mine any pending records
        if self.ledger.pending_records:
            self.ledger.mine_pending_block(miner_id=self.node_id)

        print(f"[ARIA] Node {self.node_id} stopped")
        print(f"[ARIA] Total inferences: {self.engine.total_inferences}")
        print(f"[ARIA] Tokens earned: {self.tokens_earned:.4f} ARIA")

    async def connect_to_peers(self, peers: List[str]):
        """
        Connect to a list of peers for P2P communication.

        Args:
            peers: List of "host:port" strings (e.g., ["localhost:8766"])
        """
        await self.network.bootstrap(peers)

        # Announce our shards to connected peers
        if self.network.local_shards:
            await self.network.announce_shards(self.network.local_shards)

    async def _handle_network_inference(self, data: dict) -> dict:
        """Handle inference requests from the network."""
        query = data.get("query", "")
        model_id = data.get("model_id", "aria-2b-1bit")
        max_tokens = data.get("max_tokens", 100)

        result = self.process_request(query, model_id, max_tokens)

        return {
            "request_id": result.request_id,
            "output": result.output_text,
            "tokens": result.tokens_generated,
            "latency_ms": result.latency_ms,
            "energy_mj": result.energy_mj,
            "node_id": self.node_id,
        }

    async def _handle_pipeline_forward(self, data: dict) -> dict:
        """
        Handle a pipeline forward request from another node.

        This processes the incoming activations through our local layers
        and either returns the final result or forwards to the next node.
        """
        state_dict = data.get("state", {})
        is_replica = data.get("is_replica", False)

        try:
            # Deserialize pipeline state
            state = PipelineState.from_dict(state_dict)

            # Process through our local layers
            new_state, result = self.engine.process_pipeline_stage(state)

            if result:
                # We're the final stage - return result
                # Record provenance
                record = result.to_provenance_record(state.query)
                self.ledger.add_record(record)

                # Calculate reward (split among all nodes)
                reward = self._calculate_reward(result) / len(result.nodes_used)
                self.tokens_earned += reward

                return {
                    "status": "completed",
                    "result": {
                        "request_id": result.request_id,
                        "output": result.output_text,
                        "tokens": result.tokens_generated,
                        "latency_ms": result.latency_ms,
                        "energy_mj": result.energy_mj,
                        "nodes_used": result.nodes_used,
                    }
                }
            else:
                # Forward to next stage
                next_stage = self.network.get_next_stage(
                    state.model_id,
                    new_state.current_layer
                )

                if not next_stage:
                    return {
                        "status": "error",
                        "error": f"No node found for layer {new_state.current_layer}"
                    }

                next_node_id, _, _, _, replicas = next_stage

                # Forward to next node (excluding ourselves from replicas)
                replicas = [r for r in replicas if r != self.node_id]

                response = await self.network.forward_pipeline_state(
                    next_node_id,
                    new_state.to_dict(),
                    replicas
                )

                if response:
                    return response
                else:
                    return {
                        "status": "error",
                        "error": "Failed to forward to next pipeline stage"
                    }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def process_distributed_inference(self, query: str,
                                            model_id: str = "aria-2b-1bit",
                                            max_tokens: int = 100,
                                            total_layers: int = 24
                                            ) -> Optional[InferenceResult]:
        """
        Process an inference request through the distributed pipeline.

        This orchestrates the full pipeline:
        1. Create initial pipeline state
        2. Process through local layers (if we have early layers)
        3. Forward to subsequent nodes in the chain
        4. Return final result

        This is the main entry point for distributed inference.

        Args:
            query: Input text/prompt
            model_id: Which model to use
            max_tokens: Maximum output tokens
            total_layers: Total layers in the model

        Returns:
            InferenceResult if successful, None if pipeline failed
        """
        if not self.is_running:
            raise RuntimeError("Node is not running. Call start() first.")

        # Get pipeline chain
        chain = self.network.build_pipeline_chain(model_id, total_layers)

        if not chain:
            raise ValueError(f"No pipeline chain found for model {model_id}")

        # Check if we're the first stage
        first_node_id = chain[0][0]

        # Create initial pipeline state
        state = self.engine.create_pipeline_state(
            query=query,
            model_id=model_id,
            max_tokens=max_tokens,
            total_layers=total_layers,
            originator_id=self.node_id
        )

        if first_node_id == self.node_id:
            # We're first - process locally first
            shard = self.engine.get_shard_info(model_id)
            if shard and shard.layer_start == 0:
                new_state, result = self.engine.process_pipeline_stage(state)

                if result:
                    # We have all layers - return directly
                    return result

                state = new_state

        # Find where to forward
        next_stage = self.network.get_next_stage(model_id, state.current_layer)

        if not next_stage:
            raise ValueError(
                f"No node found for layer {state.current_layer}"
            )

        next_node_id, _, _, _, replicas = next_stage

        # Forward to the pipeline
        response = await self.network.forward_pipeline_state(
            next_node_id,
            state.to_dict(),
            [r for r in replicas if r != self.node_id]
        )

        if response and response.get("status") == "completed":
            result_data = response.get("result", {})

            # Create InferenceResult from response
            result = InferenceResult(
                request_id=result_data.get("request_id", state.request_id),
                output_tokens=[],  # Not transmitted over network
                output_text=result_data.get("output", ""),
                latency_ms=result_data.get("latency_ms", 0),
                energy_mj=result_data.get("energy_mj", 0),
                nodes_used=result_data.get("nodes_used", []),
                model_id=model_id,
                tokens_generated=result_data.get("tokens", 0),
            )

            # Record provenance locally as orchestrator
            record = result.to_provenance_record(query)
            self.ledger.add_record(record)

            return result

        return None

    def process_request(self, query: str, model_id: str = "aria-2b-1bit",
                        max_tokens: int = 100) -> InferenceResult:
        """
        Process an inference request.

        This is the main work loop:
        1. Run inference through the local engine
        2. Record provenance on the ledger
        3. Submit Proof of Useful Work
        4. Calculate and add rewards

        Args:
            query: The input text/prompt
            model_id: Which model to use
            max_tokens: Maximum output length

        Returns:
            InferenceResult with output and metadata
        """
        if not self.is_running:
            raise RuntimeError("Node is not running. Call start() first.")

        # 1. Run inference
        result = self.engine.infer(
            query=query,
            model_id=model_id,
            max_tokens=max_tokens,
        )

        # 2. Record provenance
        record = result.to_provenance_record(query)
        record_hash = self.ledger.add_record(record)

        # 3. Submit Proof of Useful Work
        proof = self.pouw.create_proof(
            node_id=self.node_id,
            inference_id=result.request_id,
            query_hash=record.query_hash,
            output_hash=record.output_hash,
            model_id=model_id,
            energy_mj=result.energy_mj,
            latency_ms=result.latency_ms,
        )
        self.pouw.submit_proof(proof)

        # 4. Calculate rewards
        reward = self._calculate_reward(result)
        self.tokens_earned += reward

        return result

    async def send_inference_request(self, peer_id: str, query: str,
                                     model_id: str = "aria-2b-1bit",
                                     max_tokens: int = 100) -> Optional[dict]:
        """
        Send an inference request to a specific peer.

        Args:
            peer_id: The target peer's node ID
            query: The input text/prompt
            model_id: Which model to use
            max_tokens: Maximum output length

        Returns:
            Response dict with inference result, or None if failed
        """
        msg = self.network.create_message("inference_request", {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "query": query,
            "model_id": model_id,
            "max_tokens": max_tokens,
        })

        response = await self.network.send_to_peer(peer_id, msg)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return None
        return None

    def _calculate_reward(self, result: InferenceResult) -> float:
        """
        Calculate ARIA token reward for an inference.

        Reward = base_rate × quality_score × efficiency_bonus

        Quality: based on latency (faster = better)
        Efficiency: based on energy consumption (less = better)
        """
        base_rate = 0.001  # 0.001 ARIA per inference

        # Quality score: latency-based [0, 1]
        # Target: <1000ms = perfect, >5000ms = minimum
        quality = max(0, min(1, 1 - (result.latency_ms - 1000) / 4000))

        # Efficiency bonus: energy-based [0.5, 2.0]
        # Baseline: 150 mJ (GPU equivalent)
        if result.energy_mj > 0:
            efficiency = min(2.0, max(0.5, 150 / result.energy_mj))
        else:
            efficiency = 1.0

        return base_rate * max(quality, 0.1) * efficiency

    def get_stats(self) -> Dict:
        """Get comprehensive node statistics."""
        uptime = time.time() - self.start_time if self.start_time else 0
        engine_stats = self.engine.get_stats()
        network_stats = self.network.get_network_stats()
        ledger_stats = self.ledger.get_network_stats()

        return {
            "node_id": self.node_id,
            "is_running": self.is_running,
            "uptime_seconds": round(uptime),
            "consent": str(self.consent),
            "tokens_earned": round(self.tokens_earned, 6),
            "engine": engine_stats,
            "network": network_stats,
            "ledger": ledger_stats,
            "proofs": {
                "verified": self.pouw.verified_count,
                "rejected": self.pouw.rejected_count,
            },
            "sobriety": (
                self.sobriety.get_network_savings()
                if self.sobriety.attestations else {}
            ),
        }

    def _get_ledger_stats(self) -> Dict:
        """Get ledger statistics for CLI."""
        return self.ledger.get_network_stats()

    def _verify_ledger(self) -> Dict:
        """Verify ledger integrity for CLI."""
        valid = self.ledger.verify_chain()
        return {
            "valid": valid,
            "chain_length": len(self.ledger.chain),
            "pending_records": len(self.ledger.pending_records),
        }

    def __repr__(self) -> str:
        status = "running" if self.is_running else "stopped"
        return (
            f"ARIANode(id={self.node_id}, status={status}, "
            f"inferences={self.engine.total_inferences}, "
            f"earned={self.tokens_earned:.4f} ARIA)"
        )
