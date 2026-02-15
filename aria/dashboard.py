"""
ARIA Protocol - Real-time Monitoring Dashboard.

Provides a web-based dashboard for monitoring ARIA node status,
inference metrics, energy consumption, and peer connections.

MIT License - Anthony MURGO, 2026
"""

import asyncio
import json
import logging
import time
from collections import deque
from typing import Optional, Dict, List, Set

from aiohttp import web, WSMsgType
import websockets

logger = logging.getLogger(__name__)


class ARIADashboard:
    """
    Real-time monitoring dashboard for ARIA Protocol.

    Provides a web interface with live updates via WebSocket
    showing node status, inference metrics, energy savings,
    and peer connections.

    Example usage:
        dashboard = ARIADashboard(port=8080, node_port=8765)
        await dashboard.start()
    """

    def __init__(self, port: int = 8080, node_host: str = "localhost",
                 node_port: int = 8765):
        """
        Initialize the dashboard server.

        Args:
            port: HTTP port for the dashboard
            node_host: ARIA node WebSocket host
            node_port: ARIA node WebSocket port
        """
        self.port = port
        self.node_host = node_host
        self.node_port = node_port
        self.node_uri = f"ws://{node_host}:{node_port}"

        self.app = web.Application()
        self._setup_routes()

        self.runner: Optional[web.AppRunner] = None
        self.is_running = False
        self.start_time: Optional[float] = None

        # WebSocket clients for real-time updates
        self.ws_clients: Set[web.WebSocketResponse] = set()

        # Inference history (last 10)
        self.inference_history: deque = deque(maxlen=10)

        # Cached stats
        self._last_stats: Dict = {}
        self._stats_lock = asyncio.Lock()

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/ws", self._handle_websocket)
        self.app.router.add_get("/api/stats", self._handle_api_stats)

    async def start(self):
        """Start the dashboard server."""
        if self.is_running:
            return

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await site.start()

        self.is_running = True
        self.start_time = time.time()

        # Start background task for pushing updates
        asyncio.create_task(self._push_updates())

        print("[ARIA Dashboard] Monitoring dashboard started")
        print(f"[ARIA Dashboard] Open http://localhost:{self.port} in your browser")
        print(f"[ARIA Dashboard] Connected to ARIA node at {self.node_uri}")

    async def stop(self):
        """Stop the dashboard server."""
        if not self.is_running:
            return

        self.is_running = False

        # Close all WebSocket connections
        for ws in self.ws_clients.copy():
            await ws.close()
        self.ws_clients.clear()

        if self.runner:
            await self.runner.cleanup()

        print("[ARIA Dashboard] Server stopped")

    async def _get_node_stats(self) -> Dict:
        """Fetch stats from the ARIA node."""
        try:
            async with websockets.connect(self.node_uri, close_timeout=2) as ws:
                msg = {
                    "type": "get_stats",
                    "sender_id": "dashboard",
                    "data": {},
                    "timestamp": time.time(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                result = json.loads(response)

                if "data" in result:
                    return result["data"]
                return {}
        except Exception as e:
            logger.debug(f"Failed to fetch node stats: {e}")
            return {}

    async def _get_peers(self) -> List[Dict]:
        """Fetch peer list from the ARIA node."""
        try:
            async with websockets.connect(self.node_uri, close_timeout=2) as ws:
                msg = {
                    "type": "get_peers",
                    "sender_id": "dashboard",
                    "data": {},
                    "timestamp": time.time(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                result = json.loads(response)

                if "data" in result and "peers" in result["data"]:
                    return result["data"]["peers"]
                return []
        except Exception as e:
            logger.debug(f"Failed to fetch peers: {e}")
            return []

    async def _push_updates(self):
        """Background task to push updates to all connected clients."""
        while self.is_running:
            try:
                # Collect all stats
                stats = await self._get_node_stats()
                peers = await self._get_peers()

                # Build dashboard data
                dashboard_data = self._build_dashboard_data(stats, peers)

                # Cache stats
                async with self._stats_lock:
                    self._last_stats = dashboard_data

                # Push to all connected clients
                if self.ws_clients:
                    message = json.dumps({
                        "type": "stats_update",
                        "data": dashboard_data,
                        "timestamp": time.time()
                    })

                    disconnected = set()
                    for ws in self.ws_clients:
                        try:
                            await ws.send_str(message)
                        except Exception as e:
                            logger.debug(f"WebSocket client send failed: {e}")
                            disconnected.add(ws)

                    # Remove disconnected clients
                    self.ws_clients -= disconnected

            except Exception as e:
                logger.debug(f"Dashboard push update error: {e}")

            await asyncio.sleep(2)  # Update every 2 seconds

    def _build_dashboard_data(self, stats: Dict, peers: List[Dict]) -> Dict:
        """Build the complete dashboard data structure."""
        # Node status
        node_status = {
            "status": "running" if stats.get("is_running", False) else "stopped",
            "node_id": stats.get("node_id", "N/A"),
            "uptime_seconds": stats.get("uptime_seconds", 0),
        }

        # Engine stats
        engine = stats.get("engine", {})
        inference_stats = {
            "total_inferences": engine.get("total_inferences", 0),
            "total_energy_mj": engine.get("total_energy_mj", 0),
            "loaded_models": engine.get("loaded_models", 0),
        }

        # Contribution score
        contribution_score = stats.get("contribution_score", 0)

        # Energy savings (Proof of Sobriety)
        sobriety = stats.get("sobriety", {})
        aria_energy = sobriety.get("aria_energy_mj", inference_stats["total_energy_mj"])
        # GPU baseline: ~150mJ per inference (high-end GPU like A100)
        total_inferences = sobriety.get("total_inferences", inference_stats["total_inferences"])
        gpu_baseline = total_inferences * 150 if total_inferences > 0 else 0

        energy_stats = {
            "aria_energy_mj": aria_energy,
            "gpu_baseline_mj": gpu_baseline,
            "energy_saved_mj": max(0, gpu_baseline - aria_energy),
            "savings_percent": sobriety.get("savings_percent",
                round((1 - aria_energy / gpu_baseline) * 100, 1) if gpu_baseline > 0 else 0),
            "co2_saved_grams": sobriety.get("co2_saved_grams", 0),
        }

        # Network stats
        network = stats.get("network", {})
        network_stats = {
            "total_peers": network.get("total_peers", 0),
            "alive_peers": network.get("alive_peers", 0),
            "messages_sent": network.get("messages_sent", 0),
            "messages_received": network.get("messages_received", 0),
        }

        # Peer details
        peer_list = []
        for peer in peers:
            peer_list.append({
                "node_id": peer.get("node_id", "unknown")[:16],
                "host": peer.get("host", "?"),
                "port": peer.get("port", "?"),
                "reputation": peer.get("reputation", 0),
                "shards": len(peer.get("available_shards", [])),
            })

        # Ledger stats
        ledger = stats.get("ledger", {})

        return {
            "node": node_status,
            "inference": inference_stats,
            "contribution_score": contribution_score,
            "energy": energy_stats,
            "network": network_stats,
            "peers": peer_list,
            "ledger": {
                "chain_length": ledger.get("chain_length", 0),
                "chain_valid": ledger.get("chain_valid", True),
            },
            "inference_history": list(self.inference_history),
        }

    async def _handle_index(self, request: web.Request) -> web.Response:
        """Serve the dashboard HTML page."""
        return web.Response(
            text=DASHBOARD_HTML,
            content_type="text/html"
        )

    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.ws_clients.add(ws)

        # Send initial stats
        async with self._stats_lock:
            if self._last_stats:
                await ws.send_str(json.dumps({
                    "type": "stats_update",
                    "data": self._last_stats,
                    "timestamp": time.time()
                }))

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle any incoming messages (future expansion)
                    pass
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            self.ws_clients.discard(ws)

        return ws

    async def _handle_api_stats(self, request: web.Request) -> web.Response:
        """Handle API stats request (JSON)."""
        async with self._stats_lock:
            return web.json_response(self._last_stats)


# Embedded HTML/CSS/JS Dashboard
DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARIA Protocol - Monitoring Dashboard</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --border-color: #30363d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent-green: #3fb950;
            --accent-blue: #58a6ff;
            --accent-orange: #d29922;
            --accent-red: #f85149;
            --accent-purple: #a371f7;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.5;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
        }

        .logo-text {
            font-size: 20px;
            font-weight: 600;
        }

        .logo-sub {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .connection-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-secondary);
            border-radius: 20px;
            font-size: 14px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-red);
        }

        .status-dot.connected {
            background: var(--accent-green);
            box-shadow: 0 0 8px var(--accent-green);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .card-icon {
            width: 32px;
            height: 32px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .metric-large {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .metric-label {
            font-size: 13px;
            color: var(--text-secondary);
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
        }

        .metric-row:last-child {
            border-bottom: none;
        }

        .metric-name {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .metric-value {
            font-weight: 600;
            font-size: 14px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-badge.running {
            background: rgba(63, 185, 80, 0.15);
            color: var(--accent-green);
        }

        .status-badge.stopped {
            background: rgba(248, 81, 73, 0.15);
            color: var(--accent-red);
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
            border-radius: 4px;
            transition: width 0.5s ease;
        }

        .energy-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 16px;
        }

        .energy-box {
            padding: 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            text-align: center;
        }

        .energy-box.aria {
            border-left: 3px solid var(--accent-green);
        }

        .energy-box.gpu {
            border-left: 3px solid var(--accent-orange);
        }

        .energy-value {
            font-size: 20px;
            font-weight: 700;
        }

        .energy-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }

        .savings-highlight {
            background: linear-gradient(135deg, rgba(63, 185, 80, 0.1), rgba(88, 166, 255, 0.1));
            border: 1px solid rgba(63, 185, 80, 0.3);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            margin-top: 16px;
        }

        .savings-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--accent-green);
        }

        .peer-list {
            max-height: 200px;
            overflow-y: auto;
        }

        .peer-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .peer-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .peer-id {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            color: var(--accent-blue);
        }

        .peer-address {
            font-size: 11px;
            color: var(--text-muted);
        }

        .peer-stats {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .reputation-bar {
            width: 60px;
            height: 6px;
            background: var(--bg-primary);
            border-radius: 3px;
            overflow: hidden;
        }

        .reputation-fill {
            height: 100%;
            background: var(--accent-green);
            border-radius: 3px;
        }

        .inference-list {
            max-height: 250px;
            overflow-y: auto;
        }

        .inference-item {
            padding: 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .inference-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .inference-id {
            font-family: monospace;
            color: var(--accent-purple);
            font-size: 11px;
        }

        .inference-time {
            color: var(--text-muted);
            font-size: 11px;
        }

        .inference-metrics {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }

        .inference-metric {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .inference-metric-icon {
            font-size: 12px;
        }

        .empty-state {
            text-align: center;
            padding: 32px;
            color: var(--text-muted);
        }

        .wide-card {
            grid-column: span 2;
        }

        @media (max-width: 768px) {
            .container {
                padding: 12px;
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .wide-card {
                grid-column: span 1;
            }

            .metric-large {
                font-size: 24px;
            }

            header {
                flex-direction: column;
                align-items: flex-start;
            }

            .energy-comparison {
                grid-template-columns: 1fr;
            }
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }

        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">A</div>
                <div>
                    <div class="logo-text">ARIA Protocol</div>
                    <div class="logo-sub">Monitoring Dashboard</div>
                </div>
            </div>
            <div class="connection-status">
                <div class="status-dot" id="connectionDot"></div>
                <span id="connectionText">Connecting...</span>
            </div>
        </header>

        <div class="grid">
            <!-- Node Status -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Node Status</span>
                    <div class="card-icon">&#x26A1;</div>
                </div>
                <div style="margin-bottom: 16px;">
                    <span class="status-badge" id="nodeStatus">stopped</span>
                </div>
                <div class="metric-row">
                    <span class="metric-name">Node ID</span>
                    <span class="metric-value" id="nodeId" style="font-family: monospace; font-size: 12px;">-</span>
                </div>
                <div class="metric-row">
                    <span class="metric-name">Uptime</span>
                    <span class="metric-value" id="uptime">-</span>
                </div>
                <div class="metric-row">
                    <span class="metric-name">Models Loaded</span>
                    <span class="metric-value" id="modelsLoaded">0</span>
                </div>
            </div>

            <!-- Inferences -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Inferences</span>
                    <div class="card-icon">&#x1F9E0;</div>
                </div>
                <div class="metric-large" id="totalInferences">0</div>
                <div class="metric-label">Total Processed</div>
                <div class="metric-row" style="margin-top: 16px;">
                    <span class="metric-name">Messages Sent</span>
                    <span class="metric-value" id="messagesSent">0</span>
                </div>
                <div class="metric-row">
                    <span class="metric-name">Messages Received</span>
                    <span class="metric-value" id="messagesReceived">0</span>
                </div>
            </div>

            <!-- Contribution Score -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Contribution Score</span>
                    <div class="card-icon">&#x2B50;</div>
                </div>
                <div class="metric-large" style="color: var(--accent-purple);" id="contributionScore">0.000000</div>
                <div class="metric-label">Reputation Points</div>
                <div class="metric-row" style="margin-top: 16px;">
                    <span class="metric-name">Chain Blocks</span>
                    <span class="metric-value" id="chainLength">0</span>
                </div>
                <div class="metric-row">
                    <span class="metric-name">Chain Valid</span>
                    <span class="metric-value" id="chainValid" style="color: var(--accent-green);">-</span>
                </div>
            </div>

            <!-- Energy Consumption -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Energy Consumption</span>
                    <div class="card-icon">&#x1F50B;</div>
                </div>
                <div class="energy-comparison">
                    <div class="energy-box aria">
                        <div class="energy-value" id="ariaEnergy">0</div>
                        <div class="energy-label">ARIA (mJ)</div>
                    </div>
                    <div class="energy-box gpu">
                        <div class="energy-value" id="gpuBaseline">0</div>
                        <div class="energy-label">GPU Baseline (mJ)</div>
                    </div>
                </div>
                <div class="savings-highlight">
                    <div class="savings-value" id="savingsPercent">0%</div>
                    <div class="metric-label">Energy Savings vs GPU</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="savingsBar" style="width: 0%;"></div>
                </div>
            </div>

            <!-- Connected Peers -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Connected Peers</span>
                    <div class="card-icon">&#x1F310;</div>
                </div>
                <div style="display: flex; gap: 24px; margin-bottom: 16px;">
                    <div>
                        <div class="metric-large" id="alivePeers">0</div>
                        <div class="metric-label">Active</div>
                    </div>
                    <div>
                        <div class="metric-large" style="color: var(--text-secondary);" id="totalPeers">0</div>
                        <div class="metric-label">Total</div>
                    </div>
                </div>
                <div class="peer-list" id="peerList">
                    <div class="empty-state">No peers connected</div>
                </div>
            </div>

            <!-- Inference History -->
            <div class="card wide-card">
                <div class="card-header">
                    <span class="card-title">Recent Inferences</span>
                    <div class="card-icon">&#x1F4CA;</div>
                </div>
                <div class="inference-list" id="inferenceHistory">
                    <div class="empty-state">No recent inferences</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 10;
        const reconnectDelay = 2000;

        function formatDuration(seconds) {
            if (seconds < 60) return `${Math.floor(seconds)}s`;
            if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${mins}m`;
        }

        function formatEnergy(mj) {
            if (mj < 1000) return mj.toFixed(1);
            return (mj / 1000).toFixed(2) + 'k';
        }

        function updateUI(data) {
            // Node status
            const nodeStatus = document.getElementById('nodeStatus');
            const status = data.node?.status || 'stopped';
            nodeStatus.textContent = status;
            nodeStatus.className = `status-badge ${status}`;

            document.getElementById('nodeId').textContent = data.node?.node_id || '-';
            document.getElementById('uptime').textContent = formatDuration(data.node?.uptime_seconds || 0);
            document.getElementById('modelsLoaded').textContent = data.inference?.loaded_models || 0;

            // Inferences
            document.getElementById('totalInferences').textContent = data.inference?.total_inferences || 0;
            document.getElementById('messagesSent').textContent = data.network?.messages_sent || 0;
            document.getElementById('messagesReceived').textContent = data.network?.messages_received || 0;

            // Contribution Score
            document.getElementById('contributionScore').textContent = (data.contribution_score || 0).toFixed(6);
            document.getElementById('chainLength').textContent = data.ledger?.chain_length || 0;
            const chainValid = document.getElementById('chainValid');
            if (data.ledger?.chain_valid !== undefined) {
                chainValid.textContent = data.ledger.chain_valid ? 'Yes' : 'No';
                chainValid.style.color = data.ledger.chain_valid ? 'var(--accent-green)' : 'var(--accent-red)';
            }

            // Energy
            document.getElementById('ariaEnergy').textContent = formatEnergy(data.energy?.aria_energy_mj || 0);
            document.getElementById('gpuBaseline').textContent = formatEnergy(data.energy?.gpu_baseline_mj || 0);
            const savings = data.energy?.savings_percent || 0;
            document.getElementById('savingsPercent').textContent = `${savings.toFixed(1)}%`;
            document.getElementById('savingsBar').style.width = `${Math.min(100, savings)}%`;

            // Peers
            document.getElementById('alivePeers').textContent = data.network?.alive_peers || 0;
            document.getElementById('totalPeers').textContent = data.network?.total_peers || 0;

            const peerList = document.getElementById('peerList');
            const peers = data.peers || [];
            if (peers.length === 0) {
                peerList.innerHTML = '<div class="empty-state">No peers connected</div>';
            } else {
                peerList.innerHTML = peers.map(peer => `
                    <div class="peer-item">
                        <div class="peer-info">
                            <div class="peer-id">${peer.node_id}</div>
                            <div class="peer-address">${peer.host}:${peer.port}</div>
                        </div>
                        <div class="peer-stats">
                            <div class="reputation-bar">
                                <div class="reputation-fill" style="width: ${(peer.reputation || 0) * 100}%"></div>
                            </div>
                            <span style="font-size: 11px; color: var(--text-muted);">${peer.shards || 0} shards</span>
                        </div>
                    </div>
                `).join('');
            }

            // Inference history
            const historyList = document.getElementById('inferenceHistory');
            const history = data.inference_history || [];
            if (history.length === 0) {
                historyList.innerHTML = '<div class="empty-state">No recent inferences</div>';
            } else {
                historyList.innerHTML = history.map(inf => `
                    <div class="inference-item">
                        <div class="inference-header">
                            <span class="inference-id">${inf.request_id || 'N/A'}</span>
                            <span class="inference-time">${new Date(inf.timestamp * 1000).toLocaleTimeString()}</span>
                        </div>
                        <div class="inference-metrics">
                            <div class="inference-metric">
                                <span class="inference-metric-icon">&#x23F1;</span>
                                <span>${inf.latency_ms || 0}ms</span>
                            </div>
                            <div class="inference-metric">
                                <span class="inference-metric-icon">&#x26A1;</span>
                                <span>${formatEnergy(inf.energy_mj || 0)} mJ</span>
                            </div>
                            <div class="inference-metric">
                                <span class="inference-metric-icon">&#x1F4DD;</span>
                                <span>${inf.tokens || 0} tokens</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }

        function setConnectionStatus(connected) {
            const dot = document.getElementById('connectionDot');
            const text = document.getElementById('connectionText');

            if (connected) {
                dot.classList.add('connected');
                text.textContent = 'Connected';
                reconnectAttempts = 0;
            } else {
                dot.classList.remove('connected');
                text.textContent = 'Disconnected';
            }
        }

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                console.log('WebSocket connected');
                setConnectionStatus(true);
            };

            ws.onmessage = function(event) {
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'stats_update' && message.data) {
                        updateUI(message.data);
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };

            ws.onclose = function() {
                console.log('WebSocket disconnected');
                setConnectionStatus(false);

                // Attempt to reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Reconnecting in ${reconnectDelay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                    setTimeout(connect, reconnectDelay);
                }
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        // Start connection when page loads
        document.addEventListener('DOMContentLoaded', connect);
    </script>
</body>
</html>
'''


async def run_dashboard(port: int = 8080, node_host: str = "localhost",
                        node_port: int = 8765):
    """
    Run the monitoring dashboard server.

    This is the main entry point for running the dashboard standalone.

    Args:
        port: HTTP port for the dashboard
        node_host: ARIA node host
        node_port: ARIA node WebSocket port
    """
    dashboard = ARIADashboard(
        port=port,
        node_host=node_host,
        node_port=node_port
    )

    await dashboard.start()

    print("\nDashboard is running. Press Ctrl+C to stop.\n")
    print("-" * 50)

    # Keep running
    try:
        while dashboard.is_running:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await dashboard.stop()


if __name__ == "__main__":
    asyncio.run(run_dashboard())
