"""
ARIA Protocol Command Line Interface.

Provides commands for managing ARIA nodes, network operations,
inference requests, and ledger management.
"""

import argparse
import asyncio
import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from aria.node import ARIANode
from aria.consent import ARIAConsent, TaskType
from aria.ledger import ProvenanceLedger
from aria.network import ARIANetwork, PeerInfo
from aria.api import ARIAOpenAIServer

# State file for tracking running node
STATE_DIR = Path.home() / ".aria"
STATE_FILE = STATE_DIR / "node_state.json"
LEDGER_FILE = STATE_DIR / "ledger.json"
API_STATE_FILE = STATE_DIR / "api_state.json"


def ensure_state_dir():
    """Ensure the state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_node_state(node_id: str, port: int, pid: int):
    """Save running node state to file."""
    ensure_state_dir()
    state = {
        "node_id": node_id,
        "port": port,
        "pid": pid,
        "started_at": datetime.now().isoformat(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_node_state() -> Optional[dict]:
    """Load node state from file."""
    if not STATE_FILE.exists():
        return None
    try:
        state = json.loads(STATE_FILE.read_text())
        # Check if the process is still running
        pid = state.get("pid")
        if pid:
            try:
                os.kill(pid, 0)  # Check if process exists
            except OSError:
                # Process not running, clean up state
                STATE_FILE.unlink()
                return None
        return state
    except (json.JSONDecodeError, KeyError):
        return None


def clear_node_state():
    """Clear node state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def save_api_state(port: int, node_port: int, pid: int):
    """Save running API server state to file."""
    ensure_state_dir()
    state = {
        "port": port,
        "node_port": node_port,
        "pid": pid,
        "started_at": datetime.now().isoformat(),
    }
    API_STATE_FILE.write_text(json.dumps(state, indent=2))


def load_api_state() -> Optional[dict]:
    """Load API server state from file."""
    if not API_STATE_FILE.exists():
        return None
    try:
        state = json.loads(API_STATE_FILE.read_text())
        pid = state.get("pid")
        if pid:
            try:
                os.kill(pid, 0)
            except OSError:
                API_STATE_FILE.unlink()
                return None
        return state
    except (json.JSONDecodeError, KeyError):
        return None


def clear_api_state():
    """Clear API server state file."""
    if API_STATE_FILE.exists():
        API_STATE_FILE.unlink()


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_energy(mj: float) -> str:
    """Format energy in appropriate units."""
    if mj < 1000:
        return f"{mj:.2f} mJ"
    else:
        return f"{mj/1000:.2f} J"


class NodeManager:
    """Manages ARIA node lifecycle and state."""

    def __init__(self):
        self.node: Optional[ARIANode] = None
        self.running = False

    async def start_node(self, port: int, cpu_percent: int, schedule: str,
                         peers: list = None, model: str = None):
        """Start an ARIA node with the given configuration."""
        # Parse schedule
        consent = ARIAConsent(
            cpu_percent=cpu_percent,
            schedule=schedule,
            task_types=[TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION, TaskType.ANY],
        )

        # Create node
        self.node = ARIANode(consent=consent, port=port)

        print(f"ARIA Node Starting...")
        print(f"  Node ID: {self.node.node_id}")
        print(f"  Port: {port}")
        print(f"  CPU Limit: {cpu_percent}%")
        print(f"  Schedule: {schedule}")
        print()

        # Save state
        save_node_state(self.node.node_id, port, os.getpid())

        # Load default model if specified
        if model:
            print(f"Loading model: {model}")
            shard = self.node.load_model(
                model_id=model,
                num_layers=24,
                hidden_dim=2048,
                shard_start=0,
                shard_end=23
            )
            print(f"  Loaded shard: {shard.shard_id}")
            print(f"  Layers: {shard.layer_start}-{shard.layer_end}")
            print()

        # Start node
        await self.node.start()
        print(f"Node started on ws://0.0.0.0:{port}")

        # Connect to peers if specified
        if peers:
            print(f"\nConnecting to peers...")
            await self.node.connect_to_peers(peers)
            print(f"  Connected to {len(self.node.network.peers)} peers")

        print("\nNode is running. Press Ctrl+C to stop.\n")
        print("-" * 50)

        self.running = True

        # Keep running until interrupted
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop_node()

    async def stop_node(self):
        """Stop the running node."""
        if self.node:
            print("\nStopping node...")
            await self.node.stop()
            clear_node_state()
            print("Node stopped.")
        self.running = False


def cmd_node_start(args):
    """Handle 'aria node start' command."""
    manager = NodeManager()

    # Setup signal handlers
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler():
        manager.running = False

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    # Parse peers
    peers = args.peers.split(",") if args.peers else None

    try:
        loop.run_until_complete(
            manager.start_node(
                port=args.port,
                cpu_percent=args.cpu,
                schedule=args.schedule,
                peers=peers,
                model=args.model
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


def cmd_node_status(args):
    """Handle 'aria node status' command."""
    state = load_node_state()

    if not state:
        print("No ARIA node is currently running.")
        print("\nStart a node with:")
        print("  aria node start --port 8765")
        return 1

    print("ARIA Node Status")
    print("=" * 50)
    print(f"  Node ID:    {state['node_id']}")
    print(f"  Port:       {state['port']}")
    print(f"  PID:        {state['pid']}")
    print(f"  Started:    {state['started_at']}")

    # Calculate uptime
    started = datetime.fromisoformat(state['started_at'])
    uptime = (datetime.now() - started).total_seconds()
    print(f"  Uptime:     {format_duration(uptime)}")

    # Try to get live stats via WebSocket
    async def get_live_stats():
        try:
            import websockets
            uri = f"ws://localhost:{state['port']}"
            async with websockets.connect(uri, close_timeout=2) as ws:
                # Send stats request
                msg = {
                    "type": "get_stats",
                    "sender_id": "cli",
                    "data": {},
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                return json.loads(response)
        except Exception:
            return None

    try:
        loop = asyncio.new_event_loop()
        stats = loop.run_until_complete(get_live_stats())
        loop.close()

        if stats and "data" in stats:
            data = stats["data"]
            print()
            print("Performance Metrics")
            print("-" * 50)

            if "engine" in data:
                engine = data["engine"]
                print(f"  Inferences:     {engine.get('total_inferences', 0)}")
                print(f"  Energy Used:    {format_energy(engine.get('total_energy_mj', 0))}")
                print(f"  Models Loaded:  {engine.get('loaded_models', 0)}")

            if "tokens_earned" in data:
                print(f"  Tokens Earned:  {data['tokens_earned']:.6f} ARIA")

            print()
            print("Network")
            print("-" * 50)
            if "network" in data:
                net = data["network"]
                print(f"  Total Peers:    {net.get('total_peers', 0)}")
                print(f"  Active Peers:   {net.get('alive_peers', 0)}")
                print(f"  Messages Sent:  {net.get('messages_sent', 0)}")
                print(f"  Messages Recv:  {net.get('messages_received', 0)}")
    except Exception:
        print("\n  (Could not fetch live metrics)")

    return 0


def cmd_network_peers(args):
    """Handle 'aria network peers' command."""
    state = load_node_state()

    if not state:
        print("No ARIA node is currently running.")
        return 1

    async def get_peers():
        try:
            import websockets
            uri = f"ws://localhost:{state['port']}"
            async with websockets.connect(uri, close_timeout=2) as ws:
                msg = {
                    "type": "get_peers",
                    "sender_id": "cli",
                    "data": {},
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                return json.loads(response)
        except Exception as e:
            return {"error": str(e)}

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(get_peers())
    loop.close()

    if "error" in result:
        print(f"Error connecting to node: {result['error']}")
        return 1

    peers = result.get("data", {}).get("peers", [])

    print("Connected Peers")
    print("=" * 70)

    if not peers:
        print("  No peers connected.")
        print("\n  Connect to peers with:")
        print("    aria node start --peers host1:port1,host2:port2")
        return 0

    print(f"{'Node ID':<20} {'Host:Port':<20} {'Reputation':<12} {'Shards':<10}")
    print("-" * 70)

    for peer in peers:
        node_id = peer.get("node_id", "unknown")[:18]
        host_port = f"{peer.get('host', '?')}:{peer.get('port', '?')}"
        reputation = peer.get("reputation", 0)
        shards = len(peer.get("available_shards", []))

        rep_bar = "█" * int(reputation * 10) + "░" * (10 - int(reputation * 10))
        print(f"{node_id:<20} {host_port:<20} {rep_bar} {shards:<10}")

    print(f"\nTotal: {len(peers)} peer(s)")
    return 0


def cmd_infer(args):
    """Handle 'aria infer' command."""
    state = load_node_state()

    if not state:
        print("No ARIA node is currently running.")
        print("Start a node first with: aria node start")
        return 1

    query = args.query
    model = args.model
    max_tokens = args.max_tokens

    print(f"Sending inference request...")
    print(f"  Model: {model}")
    print(f"  Query: {query[:50]}{'...' if len(query) > 50 else ''}")
    print(f"  Max Tokens: {max_tokens}")
    print()

    async def send_inference():
        try:
            import websockets
            uri = f"ws://localhost:{state['port']}"
            async with websockets.connect(uri, close_timeout=30) as ws:
                msg = {
                    "type": "inference_request",
                    "sender_id": "cli",
                    "data": {
                        "query": query,
                        "model_id": model,
                        "max_tokens": max_tokens,
                    },
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=60)
                return json.loads(response)
        except asyncio.TimeoutError:
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": str(e)}

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(send_inference())
    loop.close()

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    data = result.get("data", {})

    print("Result")
    print("=" * 50)
    print(f"  Output: {data.get('output', 'N/A')}")
    print()
    print("Metrics")
    print("-" * 50)
    print(f"  Latency:    {data.get('latency_ms', 0):.2f} ms")
    print(f"  Energy:     {format_energy(data.get('energy_mj', 0))}")
    print(f"  Tokens:     {data.get('tokens_generated', 0)}")

    nodes = data.get("nodes_used", [])
    if nodes:
        print(f"  Nodes Used: {', '.join(nodes)}")

    return 0


def cmd_ledger_stats(args):
    """Handle 'aria ledger stats' command."""
    state = load_node_state()

    if not state:
        # Try to read from local ledger file
        if LEDGER_FILE.exists():
            try:
                ledger_data = json.loads(LEDGER_FILE.read_text())
                print("ARIA Ledger Statistics (from file)")
                print("=" * 50)
                print(f"  Chain Length:     {len(ledger_data.get('chain', []))}")
                print("\n  Note: Start a node for live statistics")
                return 0
            except Exception:
                pass

        print("No ARIA node is currently running.")
        return 1

    async def get_ledger_stats():
        try:
            import websockets
            uri = f"ws://localhost:{state['port']}"
            async with websockets.connect(uri, close_timeout=2) as ws:
                msg = {
                    "type": "get_ledger_stats",
                    "sender_id": "cli",
                    "data": {},
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                return json.loads(response)
        except Exception as e:
            return {"error": str(e)}

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(get_ledger_stats())
    loop.close()

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    stats = result.get("data", {})

    print("ARIA Ledger Statistics")
    print("=" * 50)
    print()
    print("Chain")
    print("-" * 50)
    print(f"  Blocks:           {stats.get('chain_length', 0)}")
    print(f"  Chain Valid:      {'Yes' if stats.get('chain_valid', False) else 'No'}")
    print()
    print("Inferences")
    print("-" * 50)
    print(f"  Total:            {stats.get('total_inferences', 0)}")
    print(f"  Total Tokens:     {stats.get('total_tokens_generated', 0)}")
    print(f"  Avg Latency:      {stats.get('avg_latency_ms', 0):.2f} ms")
    print()
    print("Energy")
    print("-" * 50)
    total_energy = stats.get('total_energy_joules', 0) * 1000  # Convert J to mJ
    print(f"  Total Energy:     {format_energy(total_energy)}")
    print(f"  Avg per Infer:    {format_energy(stats.get('avg_energy_per_inference_mj', 0))}")
    print()
    print("Network")
    print("-" * 50)
    print(f"  Unique Nodes:     {stats.get('unique_nodes', 0)}")
    print(f"  Unique Models:    {stats.get('unique_models', 0)}")

    return 0


def cmd_ledger_verify(args):
    """Handle 'aria ledger verify' command."""
    state = load_node_state()

    if not state:
        print("No ARIA node is currently running.")
        return 1

    print("Verifying ledger integrity...")
    print()

    async def verify_ledger():
        try:
            import websockets
            uri = f"ws://localhost:{state['port']}"
            async with websockets.connect(uri, close_timeout=2) as ws:
                msg = {
                    "type": "verify_ledger",
                    "sender_id": "cli",
                    "data": {},
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                return json.loads(response)
        except Exception as e:
            return {"error": str(e)}

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(verify_ledger())
    loop.close()

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    data = result.get("data", {})
    valid = data.get("valid", False)
    chain_length = data.get("chain_length", 0)

    if valid:
        print("Verification Result: VALID")
        print("=" * 50)
        print(f"  Chain Length:  {chain_length} blocks")
        print(f"  Status:        All blocks verified")
        print(f"  Hash Links:    Intact")
        print()
        print("  The ledger chain is cryptographically valid.")
        return 0
    else:
        print("Verification Result: INVALID")
        print("=" * 50)
        print(f"  Chain Length:  {chain_length} blocks")
        print(f"  Error:         {data.get('error', 'Unknown error')}")
        print()
        print("  WARNING: The ledger chain has been corrupted!")
        return 1


class APIServerManager:
    """Manages ARIA API server lifecycle."""

    def __init__(self):
        self.server: Optional[ARIAOpenAIServer] = None
        self.running = False

    async def start_server(self, port: int, node_host: str, node_port: int):
        """Start the OpenAI-compatible API server."""
        self.server = ARIAOpenAIServer(
            port=port,
            node_host=node_host,
            node_port=node_port
        )

        print(f"ARIA OpenAI-Compatible API Server")
        print(f"=" * 50)
        print(f"  API Port:      {port}")
        print(f"  Node Address:  {node_host}:{node_port}")
        print()

        # Check if node is reachable
        print("Checking ARIA node connection...")
        try:
            import websockets
            uri = f"ws://{node_host}:{node_port}"
            async with websockets.connect(uri, close_timeout=2) as ws:
                msg = {
                    "type": "get_stats",
                    "sender_id": "api_server",
                    "data": {},
                    "timestamp": datetime.now().timestamp(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"  Node Status:   Connected")
        except Exception as e:
            print(f"  Node Status:   Not reachable ({e})")
            print()
            print("Warning: ARIA node is not running or not reachable.")
            print(f"Start a node with: aria node start --port {node_port}")
            print()

        # Save state
        save_api_state(port, node_port, os.getpid())

        # Start server
        await self.server.start()

        print()
        print("Usage with OpenAI client:")
        print("-" * 50)
        print("  from openai import OpenAI")
        print(f'  client = OpenAI(base_url="http://localhost:{port}/v1", api_key="aria")')
        print()
        print("Server is running. Press Ctrl+C to stop.")
        print("-" * 50)

        self.running = True

        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop_server()

    async def stop_server(self):
        """Stop the API server."""
        if self.server:
            print("\nStopping API server...")
            await self.server.stop()
            clear_api_state()
            print("API server stopped.")
        self.running = False


def cmd_api_start(args):
    """Handle 'aria api start' command."""
    manager = APIServerManager()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler():
        manager.running = False

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        loop.run_until_complete(
            manager.start_server(
                port=args.port,
                node_host=args.node_host,
                node_port=args.node_port
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


def cmd_api_status(args):
    """Handle 'aria api status' command."""
    state = load_api_state()

    if not state:
        print("No ARIA API server is currently running.")
        print("\nStart an API server with:")
        print("  aria api start --port 3000")
        return 1

    print("ARIA API Server Status")
    print("=" * 50)
    print(f"  API Port:     {state['port']}")
    print(f"  Node Port:    {state['node_port']}")
    print(f"  PID:          {state['pid']}")
    print(f"  Started:      {state['started_at']}")

    # Calculate uptime
    started = datetime.fromisoformat(state['started_at'])
    uptime = (datetime.now() - started).total_seconds()
    print(f"  Uptime:       {format_duration(uptime)}")

    # Try to check health endpoint
    try:
        import urllib.request
        url = f"http://localhost:{state['port']}/health"
        with urllib.request.urlopen(url, timeout=2) as response:
            health = json.loads(response.read().decode())
            node_status = health.get("node", {}).get("status", "unknown")
            print(f"  Node Status:  {node_status}")
    except Exception:
        print(f"  Node Status:  (could not check)")

    print()
    print("Endpoints:")
    print(f"  POST http://localhost:{state['port']}/v1/chat/completions")
    print(f"  GET  http://localhost:{state['port']}/v1/models")
    print(f"  GET  http://localhost:{state['port']}/health")

    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="aria",
        description="ARIA Protocol - Decentralized AI Inference Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aria node start --port 8765 --cpu 25 --schedule "08:00-22:00"
  aria node status
  aria api start --port 3000 --node-port 8765
  aria api status
  aria network peers
  aria infer "What is artificial intelligence?" --model aria-2b-1bit
  aria ledger stats
  aria ledger verify

Documentation: https://github.com/spmfrance-cloud/aria-protocol
        """
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="<command>"
    )

    # ===== Node commands =====
    node_parser = subparsers.add_parser(
        "node",
        help="Manage ARIA node",
        description="Start, stop, and monitor ARIA nodes"
    )
    node_subparsers = node_parser.add_subparsers(
        title="node commands",
        dest="node_command",
        metavar="<subcommand>"
    )

    # node start
    node_start = node_subparsers.add_parser(
        "start",
        help="Start an ARIA node",
        description="Start an ARIA node with the specified configuration"
    )
    node_start.add_argument(
        "--port", "-p",
        type=int,
        default=8765,
        help="WebSocket port to listen on (default: 8765)"
    )
    node_start.add_argument(
        "--cpu",
        type=int,
        default=25,
        help="Maximum CPU usage percentage (default: 25)"
    )
    node_start.add_argument(
        "--schedule", "-s",
        type=str,
        default="00:00-23:59",
        help="Availability schedule in HH:MM-HH:MM format (default: 00:00-23:59)"
    )
    node_start.add_argument(
        "--peers",
        type=str,
        default=None,
        help="Comma-separated list of peers to connect to (host:port)"
    )
    node_start.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Model to load on startup (e.g., aria-2b-1bit)"
    )
    node_start.set_defaults(func=cmd_node_start)

    # node status
    node_status = node_subparsers.add_parser(
        "status",
        help="Show node status",
        description="Display status and metrics for the running ARIA node"
    )
    node_status.set_defaults(func=cmd_node_status)

    # ===== API commands =====
    api_parser = subparsers.add_parser(
        "api",
        help="Manage OpenAI-compatible API server",
        description="Start and manage the OpenAI-compatible HTTP API server"
    )
    api_subparsers = api_parser.add_subparsers(
        title="api commands",
        dest="api_command",
        metavar="<subcommand>"
    )

    # api start
    api_start = api_subparsers.add_parser(
        "start",
        help="Start the OpenAI-compatible API server",
        description="Start an HTTP server that provides OpenAI-compatible endpoints"
    )
    api_start.add_argument(
        "--port", "-p",
        type=int,
        default=3000,
        help="HTTP port for the API server (default: 3000)"
    )
    api_start.add_argument(
        "--node-host",
        type=str,
        default="localhost",
        help="ARIA node host to connect to (default: localhost)"
    )
    api_start.add_argument(
        "--node-port",
        type=int,
        default=8765,
        help="ARIA node WebSocket port (default: 8765)"
    )
    api_start.set_defaults(func=cmd_api_start)

    # api status
    api_status = api_subparsers.add_parser(
        "status",
        help="Show API server status",
        description="Display status for the running API server"
    )
    api_status.set_defaults(func=cmd_api_status)

    # ===== Network commands =====
    network_parser = subparsers.add_parser(
        "network",
        help="Network operations",
        description="Manage network connections and peer discovery"
    )
    network_subparsers = network_parser.add_subparsers(
        title="network commands",
        dest="network_command",
        metavar="<subcommand>"
    )

    # network peers
    network_peers = network_subparsers.add_parser(
        "peers",
        help="List connected peers",
        description="Display all connected peers with their status"
    )
    network_peers.set_defaults(func=cmd_network_peers)

    # ===== Infer command =====
    infer_parser = subparsers.add_parser(
        "infer",
        help="Send inference request",
        description="Send an inference request to the ARIA network"
    )
    infer_parser.add_argument(
        "query",
        type=str,
        help="The query to process"
    )
    infer_parser.add_argument(
        "--model", "-m",
        type=str,
        default="aria-2b-1bit",
        help="Model to use for inference (default: aria-2b-1bit)"
    )
    infer_parser.add_argument(
        "--max-tokens", "-t",
        type=int,
        default=100,
        help="Maximum tokens to generate (default: 100)"
    )
    infer_parser.set_defaults(func=cmd_infer)

    # ===== Ledger commands =====
    ledger_parser = subparsers.add_parser(
        "ledger",
        help="Ledger operations",
        description="Manage and query the provenance ledger"
    )
    ledger_subparsers = ledger_parser.add_subparsers(
        title="ledger commands",
        dest="ledger_command",
        metavar="<subcommand>"
    )

    # ledger stats
    ledger_stats = ledger_subparsers.add_parser(
        "stats",
        help="Show ledger statistics",
        description="Display statistics from the provenance ledger"
    )
    ledger_stats.set_defaults(func=cmd_ledger_stats)

    # ledger verify
    ledger_verify = ledger_subparsers.add_parser(
        "verify",
        help="Verify ledger integrity",
        description="Verify the cryptographic integrity of the ledger chain"
    )
    ledger_verify.set_defaults(func=cmd_ledger_verify)

    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Show help if no command provided
    if args.command is None:
        parser.print_help()
        return 0

    # Handle subcommands that need their own help
    if args.command == "node" and getattr(args, "node_command", None) is None:
        parser.parse_args(["node", "--help"])
        return 0

    if args.command == "api" and getattr(args, "api_command", None) is None:
        parser.parse_args(["api", "--help"])
        return 0

    if args.command == "network" and getattr(args, "network_command", None) is None:
        parser.parse_args(["network", "--help"])
        return 0

    if args.command == "ledger" and getattr(args, "ledger_command", None) is None:
        parser.parse_args(["ledger", "--help"])
        return 0

    # Execute the command
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
