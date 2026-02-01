"""
ARIA Protocol - P2P Network Layer
Handles node discovery, shard location, and inference routing.
Real WebSocket-based implementation with asyncio.

MIT License - Anthony MURGO, 2026
"""

import asyncio
import json
import hashlib
import time
import random
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Callable, Set

try:
    import websockets
    from websockets.asyncio.server import serve
    from websockets.asyncio.client import connect
except ImportError:
    raise ImportError("websockets is required: pip install websockets")

from aria.consent import ARIAConsent, TaskType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aria.network")


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

    def to_dict(self) -> dict:
        """Convert to dictionary for network transmission."""
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "consent": self.consent.to_dict() if self.consent else None,
            "reputation": self.reputation,
            "available_shards": self.available_shards,
            "total_inferences": self.total_inferences,
            "avg_latency_ms": self.avg_latency_ms,
            "energy_efficiency": self.energy_efficiency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PeerInfo":
        """Create PeerInfo from dictionary."""
        consent = None
        if data.get("consent"):
            consent = ARIAConsent.from_dict(data["consent"])
        return cls(
            node_id=data["node_id"],
            host=data.get("host", "localhost"),
            port=data.get("port", 8765),
            consent=consent,
            reputation=data.get("reputation", 1.0),
            available_shards=data.get("available_shards", []),
            total_inferences=data.get("total_inferences", 0),
            avg_latency_ms=data.get("avg_latency_ms", 0.0),
            energy_efficiency=data.get("energy_efficiency", 1.0),
        )


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
    The ARIA peer-to-peer network with real WebSocket connections.

    Manages node discovery, routing tables, and inference
    request matching based on consent parameters.

    Usage:
        network = ARIANetwork(node_id="my_node", port=8765)
        await network.start()
        await network.bootstrap(["localhost:8766", "localhost:8767"])

        # Route an inference request
        peers = network.find_peers_for_request(request)
    """

    HEARTBEAT_INTERVAL = 30  # seconds
    RECONNECT_DELAY = 5      # seconds

    def __init__(self, node_id: str, host: str = "0.0.0.0", port: int = 8765,
                 consent: Optional[ARIAConsent] = None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.consent = consent

        # Routing table
        self.peers: Dict[str, PeerInfo] = {}

        # Shard registry: model_shard_id -> list of node_ids
        self.shard_registry: Dict[str, List[str]] = {}

        # Message handlers
        self._handlers: Dict[str, Callable] = {}

        # Network stats
        self.messages_sent = 0
        self.messages_received = 0

        # WebSocket connections
        self._server = None
        self._connections: Dict[str, websockets.asyncio.client.ClientConnection] = {}
        self._running = False
        self._tasks: Set[asyncio.Task] = set()

        # Locks for connection access (prevent concurrent recv)
        self._connection_locks: Dict[str, asyncio.Lock] = {}

        # Available shards on this node
        self.local_shards: List[str] = []

        # Inference request handler callback
        self._inference_callback: Optional[Callable] = None

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register built-in message handlers."""
        self._handlers["ping"] = self._handle_ping
        self._handlers["pong"] = self._handle_pong
        self._handlers["peer_announce"] = self._handle_peer_announce
        self._handlers["shard_announce"] = self._handle_shard_announce
        self._handlers["inference_request"] = self._handle_inference_request
        self._handlers["get_peers"] = self._handle_get_peers

    def set_inference_callback(self, callback: Callable):
        """Set callback for handling inference requests."""
        self._inference_callback = callback

    # ==========================================
    # WEBSOCKET SERVER
    # ==========================================

    async def start(self):
        """Start the WebSocket server and background tasks."""
        if self._running:
            return

        self._running = True

        # Start WebSocket server
        self._server = await serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=30,
        )

        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._tasks.add(heartbeat_task)
        heartbeat_task.add_done_callback(self._tasks.discard)

        logger.info(f"[{self.node_id}] Network started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server and all connections."""
        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Close all client connections
        for node_id, ws in list(self._connections.items()):
            try:
                await ws.close()
            except Exception:
                pass
        self._connections.clear()
        self._connection_locks.clear()

        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        logger.info(f"[{self.node_id}] Network stopped")

    async def _handle_connection(self, websocket):
        """Handle incoming WebSocket connections."""
        peer_id = None
        try:
            async for message in websocket:
                response = await self.handle_message(message)
                if response:
                    await websocket.send(response)

                    # Track the connection by peer_id if available
                    try:
                        msg = json.loads(message)
                        sender_id = msg.get("sender_id")
                        if sender_id and sender_id not in self._connections:
                            peer_id = sender_id
                    except:
                        pass

        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"[{self.node_id}] Connection closed")
        except Exception as e:
            logger.error(f"[{self.node_id}] Connection error: {e}")

    # ==========================================
    # WEBSOCKET CLIENT
    # ==========================================

    async def connect_to_peer(self, host: str, port: int) -> bool:
        """Connect to a peer node."""
        uri = f"ws://{host}:{port}"

        try:
            ws = await connect(uri, ping_interval=20, ping_timeout=30)

            # Send peer_announce to introduce ourselves
            announce_msg = self.create_message("peer_announce", {
                "node_id": self.node_id,
                "host": "localhost",  # Our host for others to connect back
                "port": self.port,
                "consent": self.consent.to_dict() if self.consent else None,
                "shards": self.local_shards,
            })
            await ws.send(announce_msg)

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            resp_data = json.loads(response)

            if resp_data.get("status") == "accepted":
                # Store connection with its lock
                peer_id = resp_data.get("peer_id", f"{host}:{port}")
                self._connections[peer_id] = ws
                self._connection_locks[peer_id] = asyncio.Lock()

                # Add to peers
                self.add_peer(PeerInfo(
                    node_id=peer_id,
                    host=host,
                    port=port,
                ))

                logger.info(f"[{self.node_id}] Connected to peer {peer_id}")
                return True

            await ws.close()
            return False

        except asyncio.TimeoutError:
            logger.warning(f"[{self.node_id}] Connection timeout to {uri}")
            return False
        except Exception as e:
            logger.warning(f"[{self.node_id}] Failed to connect to {uri}: {e}")
            return False

    async def send_to_peer(self, peer_id: str, message: str) -> Optional[str]:
        """Send a message to a specific peer and wait for response."""
        ws = self._connections.get(peer_id)
        if not ws:
            # Try to connect if we have peer info
            if peer_id in self.peers:
                peer = self.peers[peer_id]
                if await self.connect_to_peer(peer.host, peer.port):
                    ws = self._connections.get(peer_id)

        if not ws:
            return None

        # Get or create lock for this connection
        if peer_id not in self._connection_locks:
            self._connection_locks[peer_id] = asyncio.Lock()

        lock = self._connection_locks[peer_id]

        try:
            async with lock:
                await ws.send(message)
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                return response
        except Exception as e:
            logger.error(f"[{self.node_id}] Send failed to {peer_id}: {e}")
            return None

    async def broadcast(self, message: str):
        """Broadcast a message to all connected peers (fire-and-forget)."""
        for peer_id, ws in list(self._connections.items()):
            try:
                # Fire and forget - don't wait for response
                await ws.send(message)
            except Exception:
                pass

    # ==========================================
    # BOOTSTRAP & DISCOVERY
    # ==========================================

    async def bootstrap(self, seed_peers: List[str]):
        """
        Bootstrap the network by connecting to known seed peers.

        Args:
            seed_peers: List of "host:port" strings
        """
        logger.info(f"[{self.node_id}] Bootstrapping with {len(seed_peers)} seed peers")

        for peer_addr in seed_peers:
            try:
                host, port = peer_addr.split(":")
                port = int(port)

                # Skip self
                if port == self.port:
                    continue

                await self.connect_to_peer(host, port)
            except ValueError:
                logger.warning(f"[{self.node_id}] Invalid peer address: {peer_addr}")

        # Request peer lists from connected peers
        await self._discover_more_peers()

    async def _discover_more_peers(self):
        """Ask connected peers for their peer lists."""
        # Skip discovery for now - nodes are already connected via bootstrap
        # This prevents concurrent access issues during initial setup
        pass

    # ==========================================
    # HEARTBEAT
    # ==========================================

    async def _heartbeat_loop(self):
        """Send periodic heartbeats to all peers."""
        while self._running:
            try:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)

                if not self._running:
                    break

                # Send ping to all connected peers
                ping_msg = self.create_message("ping", {"timestamp": time.time()})

                for peer_id in list(self._connections.keys()):
                    try:
                        # Use a short timeout for heartbeats
                        response = await asyncio.wait_for(
                            self.send_to_peer(peer_id, ping_msg),
                            timeout=5.0
                        )
                        if response:
                            try:
                                data = json.loads(response)
                                if data.get("type") == "pong":
                                    if peer_id in self.peers:
                                        self.peers[peer_id].last_seen = time.time()
                            except json.JSONDecodeError:
                                pass
                    except asyncio.TimeoutError:
                        logger.debug(f"[{self.node_id}] Heartbeat timeout for {peer_id}")
                    except Exception:
                        pass

                # Prune dead peers
                self.prune_dead_peers()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.node_id}] Heartbeat error: {e}")

    # ==========================================
    # PEER MANAGEMENT
    # ==========================================

    def add_peer(self, peer: PeerInfo):
        """Add or update a peer in the routing table."""
        peer.last_seen = time.time()
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

        # Clean up connection and lock
        self._connection_locks.pop(node_id, None)
        if node_id in self._connections:
            ws = self._connections.pop(node_id)
            asyncio.create_task(ws.close())

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

    async def _handle_pong(self, sender_id: str, data: dict) -> dict:
        """Handle pong response - update peer last_seen."""
        if sender_id in self.peers:
            self.peers[sender_id].last_seen = time.time()
        return {}  # No response needed

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

        logger.info(f"[{self.node_id}] Peer announced: {peer.node_id}")

        return {
            "status": "accepted",
            "peer_count": len(self.peers),
            "peer_id": self.node_id,
        }

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

        # Return empty to avoid cluttering the response queue (broadcast message)
        return {}

    async def _handle_inference_request(self, sender_id: str, data: dict) -> dict:
        """Handle an incoming inference request."""
        if self._inference_callback:
            try:
                result = await self._inference_callback(data)
                return {"status": "completed", "result": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {"status": "received", "request_id": data.get("request_id")}

    async def _handle_get_peers(self, sender_id: str, data: dict) -> dict:
        """Return list of known peers."""
        peer_list = [p.to_dict() for p in self.get_alive_peers() if p.node_id != sender_id]
        return {"peers": peer_list}

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
                if response:
                    return json.dumps(response)
                return ""
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

    async def announce_shards(self, shard_ids: List[str]):
        """Announce available shards to all connected peers."""
        self.local_shards = shard_ids
        msg = self.create_message("shard_announce", {"shard_ids": shard_ids})
        await self.broadcast(msg)

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
            "connected_peers": len(self._connections),
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
            f"connected={stats['connected_peers']}, shards={stats['total_shards_tracked']})"
        )
