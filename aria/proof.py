"""
ARIA Protocol - Proof Mechanisms
Proof of Useful Work (PoUW): Mining IS inference.
Proof of Sobriety: Verifiable energy efficiency attestation.

MIT License - Anthony MURGO, 2026
"""

import hashlib
import json
import time
import os
import platform
from dataclasses import dataclass, asdict
from typing import Optional, Dict


@dataclass
class UsefulWorkProof:
    """
    Proof that a node performed useful inference work.
    
    Unlike Bitcoin's PoW where computation is wasted on finding
    arbitrary hashes, ARIA's PoUW proves that the node performed
    actual AI inference that served a user's request.
    """
    node_id: str
    inference_id: str       # Reference to the inference record
    query_hash: str         # Hash of input (privacy preserved)
    output_hash: str        # Hash of output
    model_id: str           # Model used
    energy_mj: int          # Energy consumed
    latency_ms: int         # Time taken
    timestamp: float        # When the work was done
    nonce: int = 0          # For chain inclusion
    
    def compute_proof_hash(self) -> str:
        """Compute the proof hash."""
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify(self) -> bool:
        """
        Verify this proof is valid.
        
        In production, verification includes:
        1. Re-running the inference on a subset of validators
        2. Checking the output hash matches
        3. Verifying energy claims against hardware capabilities
        4. Cross-referencing with the provenance ledger
        
        This reference implementation does basic structural checks.
        """
        # Check all required fields are present
        if not all([self.node_id, self.inference_id, self.query_hash, 
                    self.output_hash, self.model_id]):
            return False
        
        # Check energy is reasonable (not suspiciously low or high)
        if self.energy_mj < 0 or self.energy_mj > 1_000_000:  # 0 to 1000J
            return False
        
        # Check latency is reasonable
        if self.latency_ms < 0 or self.latency_ms > 300_000:  # 0 to 5 min
            return False
        
        # Check timestamp is recent (within 1 hour)
        if abs(time.time() - self.timestamp) > 3600:
            return False
        
        return True


class ProofOfUsefulWork:
    """
    ARIA's Proof of Useful Work consensus mechanism.
    
    The key innovation: mining IS inference.
    Instead of wasting energy on arbitrary computation,
    nodes prove they did useful AI inference work.
    
    Block producers are selected based on the quantity
    and quality of inference work they've performed.
    """
    
    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self.proofs: list = []
        self.verified_count = 0
        self.rejected_count = 0
    
    def create_proof(self, node_id: str, inference_id: str,
                     query_hash: str, output_hash: str,
                     model_id: str, energy_mj: int,
                     latency_ms: int) -> UsefulWorkProof:
        """Create a new proof of useful work."""
        proof = UsefulWorkProof(
            node_id=node_id,
            inference_id=inference_id,
            query_hash=query_hash,
            output_hash=output_hash,
            model_id=model_id,
            energy_mj=energy_mj,
            latency_ms=latency_ms,
            timestamp=time.time(),
        )
        return proof
    
    def submit_proof(self, proof: UsefulWorkProof) -> bool:
        """
        Submit a proof for verification and inclusion.
        Returns True if the proof is accepted.
        """
        if proof.verify():
            self.proofs.append(proof)
            self.verified_count += 1
            return True
        else:
            self.rejected_count += 1
            return False
    
    def select_block_producer(self) -> Optional[str]:
        """
        Select the next block producer based on useful work.
        
        The node with the most verified useful work in the
        current epoch gets to produce the next block.
        """
        if not self.proofs:
            return None
        
        # Count proofs per node
        work_count: Dict[str, int] = {}
        for proof in self.proofs:
            work_count[proof.node_id] = work_count.get(proof.node_id, 0) + 1
        
        # Select node with most work
        return max(work_count, key=work_count.get)


@dataclass
class SobrietyAttestation:
    """
    A verifiable attestation of a node's energy consumption.
    
    This enables the Proof of Sobriety: a mechanism for
    proving that ARIA nodes consume less energy than
    centralized alternatives for equivalent work.
    """
    node_id: str
    period_start: float       # Measurement period start
    period_end: float         # Measurement period end
    total_inferences: int     # Inferences completed
    total_energy_mj: int      # Total energy consumed
    hardware_type: str        # CPU model/type
    os_info: str              # Operating system
    
    @property
    def energy_per_inference_mj(self) -> float:
        """Average energy per inference in millijoules."""
        if self.total_inferences == 0:
            return 0
        return self.total_energy_mj / self.total_inferences
    
    @property
    def efficiency_rating(self) -> str:
        """
        Human-readable efficiency rating.
        Based on energy per inference compared to GPU baseline.
        
        GPU baseline: ~150 mJ per inference (NVIDIA A100)
        """
        mj = self.energy_per_inference_mj
        if mj == 0:
            return "N/A"
        elif mj < 30:
            return "A+ (Exceptional)"
        elif mj < 50:
            return "A (Excellent)"
        elif mj < 100:
            return "B (Good)"
        elif mj < 150:
            return "C (Average - GPU baseline)"
        else:
            return "D (Below average)"
    
    def to_hash(self) -> str:
        """Hash for on-chain recording."""
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class ProofOfSobriety:
    """
    ARIA's Proof of Sobriety mechanism.
    
    Provides verifiable evidence that the ARIA network
    consumes less energy per inference than centralized
    alternatives. This is recorded on-chain for transparency.
    
    Energy measurement methods:
    - Linux: Reading from /sys/class/powercap/intel-rapl (RAPL)
    - macOS: Using powermetrics
    - Fallback: Estimation based on CPU TDP and utilization
    
    Usage:
        sobriety = ProofOfSobriety(node_id="my_node")
        sobriety.start_measurement()
        # ... do inference work ...
        attestation = sobriety.end_measurement(inferences_done=42)
    """
    
    # Centralized GPU baseline: ~150 mJ per inference
    GPU_BASELINE_MJ = 150
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.measurement_start: Optional[float] = None
        self.energy_start_mj: Optional[float] = None
        self.attestations: list = []
    
    def start_measurement(self):
        """Begin an energy measurement period."""
        self.measurement_start = time.time()
        self.energy_start_mj = self._read_energy_counter()
    
    def end_measurement(self, inferences_done: int) -> SobrietyAttestation:
        """
        End measurement and produce a sobriety attestation.
        
        Args:
            inferences_done: Number of inferences completed during period
            
        Returns:
            SobrietyAttestation with energy data
        """
        if self.measurement_start is None:
            raise RuntimeError("No measurement in progress. Call start_measurement() first.")
        
        energy_end = self._read_energy_counter()
        
        # Calculate energy consumed
        if self.energy_start_mj is not None and energy_end is not None:
            total_energy = int(energy_end - self.energy_start_mj)
        else:
            # Fallback: estimate based on time and CPU TDP
            elapsed = time.time() - self.measurement_start
            total_energy = int(self._estimate_energy(elapsed, inferences_done))
        
        attestation = SobrietyAttestation(
            node_id=self.node_id,
            period_start=self.measurement_start,
            period_end=time.time(),
            total_inferences=inferences_done,
            total_energy_mj=max(total_energy, 0),
            hardware_type=self._get_hardware_type(),
            os_info=f"{platform.system()} {platform.release()}",
        )
        
        self.attestations.append(attestation)
        self.measurement_start = None
        self.energy_start_mj = None
        
        return attestation
    
    def _read_energy_counter(self) -> Optional[float]:
        """
        Read hardware energy counter.
        
        Linux: Intel RAPL (Running Average Power Limit)
        Returns energy in millijoules, or None if unavailable.
        """
        rapl_path = "/sys/class/powercap/intel-rapl:0/energy_uj"
        
        try:
            if os.path.exists(rapl_path):
                with open(rapl_path, 'r') as f:
                    energy_uj = int(f.read().strip())
                    return energy_uj / 1000.0  # Convert μJ to mJ
        except (IOError, ValueError):
            pass
        
        return None
    
    def _estimate_energy(self, elapsed_seconds: float, 
                         inferences: int) -> float:
        """
        Estimate energy when hardware counters are unavailable.
        
        Based on BitNet benchmarks:
        - 1-bit inference on CPU: ~28 mJ per inference (2B model)
        - Typical idle CPU: ~5W
        """
        inference_energy = inferences * 28  # 28 mJ per inference
        idle_energy = elapsed_seconds * 5 * 1000  # 5W idle in mJ
        
        # Inference energy is added on top of idle
        return inference_energy + idle_energy * 0.1  # 10% idle overhead
    
    def _get_hardware_type(self) -> str:
        """Detect hardware type."""
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", 'r') as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            return f"{platform.processor() or platform.machine()}"
        except:
            return "unknown"
    
    def get_network_savings(self) -> Dict:
        """
        Calculate how much energy the network saves
        compared to centralized GPU inference.
        """
        if not self.attestations:
            return {"error": "No attestations available"}
        
        total_inferences = sum(a.total_inferences for a in self.attestations)
        total_energy = sum(a.total_energy_mj for a in self.attestations)
        
        gpu_equivalent = total_inferences * self.GPU_BASELINE_MJ
        savings = gpu_equivalent - total_energy
        savings_percent = (savings / gpu_equivalent * 100) if gpu_equivalent > 0 else 0
        
        return {
            "total_inferences": total_inferences,
            "aria_energy_mj": total_energy,
            "gpu_equivalent_mj": gpu_equivalent,
            "energy_saved_mj": max(savings, 0),
            "savings_percent": round(max(savings_percent, 0), 1),
            "co2_saved_grams": max(savings, 0) * 0.0004,  # ~0.4g CO2 per kJ
        }
