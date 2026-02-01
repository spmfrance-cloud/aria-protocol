"""
ARIA Protocol - P2P Network Layer
Handles node discovery, shard location, and inference routing.
Based on a simplified Kademlia-style DHT.

MIT License - Anthony MURGO, 2026
"""

import asyncio
import json
import hashlib
import time
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Callable
from aria.consent import ARIAConsent, TaskType


@dataclass
class PeerInfo:
    """Information about a peer in the network."""
    node_id: str
    host: str
    port: int
    consent: Optional[ARIAConsent] = None
    reputation: float = 1.0          # [0, 1] reliability score
    available_shards: List[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)
    total_inferences: int = 0
    avg_latency_ms: float = 0.0
    energy_efficiency: float = 1.0   # Lower is better
    
    @property
    def is_alive(self) -> bool:
        """Consider a peer dead if not seen for 5 minutes."""
        return (time.time() - self.last_seen) < 300
    
    def quality_score(self) -> float:
        """
        Compute a composite quality score for routing decisions.
        Higher is better.
        """
        uptime_factor = min(self.reputation, 1.0)
        latency_factor = max(0, 1.0 - (self.avg_latency_ms / 5000))
        efficiency_factor = 1.0 / max(self.energy_efficiency, 0.1)
        
        return uptime_factor * 0.4 + latency_factor * 0.3 + efficiency_factor * 0.3


@dataclass 
class InferenceRequest:
    """A request for distributed inference."""
    request_id: str
    query: str
    model_id: str
    task_type: TaskType = TaskType.TEXT_GENERATION
    max_tokens: int = 256
    temperature: float = 0.7
    ram_mb: int = 512
    reward: float = 0.01  # ARIA tokens offered
    timestamp: float = field(default_factory=time.time)
    
    def to_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True, default=str).encode()
        ).hexdigest()


class ARIANetwork:
    """
    The ARIA peer-to-peer network.
    
    Manages node discovery, routing tables, and inference
    request matching based on consent parameters.
    
    Usage:
        network = ARIANetwork(node_id="my_node", port=8765)
        await network.start()
        await network.discover_peers(bootstrap=["peer1:8765"])
        
        # Route an inference request
        peers = network.find_peers_for_request(request)
    """
    
    def __init__(self, node_id: str, host: str = "0.0.0.0", port: int = 8765):
        self.node_id = node_id
        self.host = host
        self.port = port
        
        # Routing table
        self.peers: Dict[str, PeerInfo] = {}
        
        # Shard registry: model_shard_id -> list of node_ids
        self.shard_registry: Dict[str, List[str]] = {}
        
        # Message handlers
        self._handlers: Dict[str, Callable] = {}
        
        # Network stats
        self.messages_sent = 0
        self.messages_received = 0
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register built-in message handlers."""
        self._handlers["ping"] = self._handle_ping
        self._handlers["peer_announce"] = self._handle_peer_announce
        self._handlers["shard_announce"] = self._handle_shard_announce
        self._handlers["inference_request"] = self._handle_inference_request
    
    # ==========================================
    # PEER MANAGEMENT
    # ==========================================
    
    def add_peer(self, peer: PeerInfo):
        """Add or update a peer in the routing table."""
        self.peers[peer.node_id] = peer
        
        # Update shard registry
        for shard_id in peer.available_shards:
            if shard_id not in self.shard_registry:
                self.shard_registry[shard_id] = []
            if peer.node_id not in self.shard_registry[shard_id]:
                self.shard_registry[shard_id].append(peer.node_id)
    
    def remove_peer(self, node_id: str):
        """Remove a peer from the routing table."""
        if node_id in self.peers:
            peer = self.peers.pop(node_id)
            # Clean shard registry
            for shard_id in peer.available_shards:
                if shard_id in self.shard_registry:
                    self.shard_registry[shard_id] = [
                        nid for nid in self.shard_registry[shard_id] 
                        if nid != node_id
                    ]
    
    def get_alive_peers(self) -> List[PeerInfo]:
        """Get all peers that are currently alive."""
        return [p for p in self.peers.values() if p.is_alive]
    
    def prune_dead_peers(self):
        """Remove peers that haven't been seen recently."""
        dead = [nid for nid, p in self.peers.items() if not p.is_alive]
        for nid in dead:
            self.remove_peer(nid)
    
    # ==========================================
    # CONSENT-BASED ROUTING
    # ==========================================
    
    def find_peers_for_request(self, request: InferenceRequest) -> List[PeerInfo]:
        """
        Find peers that match an inference request based on:
        1. Consent parameters (schedule, task type, resources)
        2. Available model shards
        3. Quality score (reputation, latency, efficiency)
        
        Returns peers sorted by quality score (best first).
        This is the core routing algorithm of ARIA.
        """
        matching_peers = []
        
        for peer in self.get_alive_peers():
            # Check consent
            if peer.consent is None:
                continue
            
            req_dict = {
                "task_type": request.task_type,
                "ram_mb": request.ram_mb,
                "reward": request.reward,
            }
            
            if not peer.consent.matches_request(req_dict):
                continue
            
            # Check if peer has relevant shards
            # (simplified: check if any shard matches model_id prefix)
            has_shard = any(
                s.startswith(request.model_id) 
                for s in peer.available_shards
            ) if peer.available_shards else True  # If no shards listed, assume available
            
            if not has_shard:
                continue
            
            matching_peers.append(peer)
        
        # Sort by quality score (best first)
        matching_peers.sort(key=lambda p: p.quality_score(), reverse=True)
        
        return matching_peers
    
    def find_shard_holders(self, shard_id: str) -> List[PeerInfo]:
        """Find all peers holding a specific model shard."""
        node_ids = self.shard_registry.get(shard_id, [])
        return [
            self.peers[nid] for nid in node_ids 
            if nid in self.peers and self.peers[nid].is_alive
        ]
    
    # ==========================================
    # MESSAGE HANDLING
    # ==========================================
    
    async def _handle_ping(self, sender_id: str, data: dict) -> dict:
        """Respond to ping with pong + our info."""
        return {
            "type": "pong",
            "node_id": self.node_id,
            "timestamp": time.time(),
            "peer_count": len(self.get_alive_peers()),
        }
    
    async def _handle_peer_announce(self, sender_id: str, data: dict) -> dict:
        """Handle a new peer announcing itself."""
        consent_data = data.get("consent")
        consent = ARIAConsent.from_dict(consent_data) if consent_data else None
        
        peer = PeerInfo(
            node_id=data["node_id"],
            host=data.get("host", "unknown"),
            port=data.get("port", 8765),
            consent=consent,
            available_shards=data.get("shards", []),
        )
        self.add_peer(peer)
        
        return {"status": "accepted", "peer_count": len(self.peers)}
    
    async def _handle_shard_announce(self, sender_id: str, data: dict) -> dict:
        """Handle a node announcing available shards."""
        shard_ids = data.get("shard_ids", [])
        
        if sender_id in self.peers:
            self.peers[sender_id].available_shards = shard_ids
            for sid in shard_ids:
                if sid not in self.shard_registry:
                    self.shard_registry[sid] = []
                if sender_id not in self.shard_registry[sid]:
                    self.shard_registry[sid].append(sender_id)
        
        return {"status": "registered", "shards": len(shard_ids)}
    
    async def _handle_inference_request(self, sender_id: str, data: dict) -> dict:
        """Handle an incoming inference request."""
        # This is delegated to the node's inference engine
        return {"status": "received", "request_id": data.get("request_id")}
    
    async def handle_message(self, raw_message: str) -> str:
        """
        Process an incoming message and return a response.
        Messages are JSON with {type, sender_id, data}.
        """
        self.messages_received += 1
        
        try:
            msg = json.loads(raw_message)
            msg_type = msg.get("type", "unknown")
            sender_id = msg.get("sender_id", "unknown")
            data = msg.get("data", {})
            
            # Update last_seen for sender
            if sender_id in self.peers:
                self.peers[sender_id].last_seen = time.time()
            
            handler = self._handlers.get(msg_type)
            if handler:
                response = await handler(sender_id, data)
                return json.dumps(response)
            else:
                return json.dumps({"error": f"Unknown message type: {msg_type}"})
        
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON"})
    
    def create_message(self, msg_type: str, data: dict) -> str:
        """Create a properly formatted ARIA protocol message."""
        self.messages_sent += 1
        return json.dumps({
            "type": msg_type,
            "sender_id": self.node_id,
            "data": data,
            "timestamp": time.time(),
            "protocol": "aria/0.1",
        })
    
    # ==========================================
    # NETWORK STATS
    # ==========================================
    
    def get_network_stats(self) -> dict:
        """Get current network statistics."""
        alive_peers = self.get_alive_peers()
        return {
            "node_id": self.node_id,
            "total_peers": len(self.peers),
            "alive_peers": len(alive_peers),
            "total_shards_tracked": sum(len(v) for v in self.shard_registry.values()),
            "unique_models": len(self.shard_registry),
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "avg_peer_reputation": (
                sum(p.reputation for p in alive_peers) / len(alive_peers)
                if alive_peers else 0
            ),
        }
    
    def __repr__(self) -> str:
        stats = self.get_network_stats()
        return (
            f"ARIANetwork(id={self.node_id}, peers={stats['alive_peers']}, "
            f"shards={stats['total_shards_tracked']})"
        )
