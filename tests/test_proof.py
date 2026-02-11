"""Tests for the ARIA proof module."""

import pytest
import time
from aria.proof import UsefulWorkProof, ProofOfUsefulWork, SobrietyAttestation, ProofOfSobriety


class TestUsefulWorkProof:
    """Tests for UsefulWorkProof dataclass."""

    def test_proof_creation(self):
        """Test creating a useful work proof."""
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time()
        )
        assert proof.node_id == "node1"
        assert proof.inference_id == "inf-123"
        assert proof.energy_mj == 50
        assert proof.latency_ms == 100
        assert proof.nonce == 0

    def test_proof_compute_hash(self):
        """Test computing proof hash."""
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100,
            timestamp=1000.0
        )
        hash1 = proof.compute_proof_hash()
        hash2 = proof.compute_proof_hash()

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_proof_verify_valid(self):
        """Test verifying a valid proof."""
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time()
        )
        assert proof.verify() is True

    def test_proof_verify_invalid_energy(self):
        """Test that proof with invalid energy fails verification."""
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=-10,  # Invalid negative energy
            latency_ms=100,
            timestamp=time.time()
        )
        assert proof.verify() is False

    def test_proof_verify_invalid_latency(self):
        """Test that proof with invalid latency fails verification."""
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=-5,  # Invalid negative latency
            timestamp=time.time()
        )
        assert proof.verify() is False


class TestProofOfUsefulWork:
    """Tests for ProofOfUsefulWork class."""

    def test_pouw_creation(self):
        """Test creating a PoUW instance."""
        pouw = ProofOfUsefulWork(difficulty=2)
        assert pouw.difficulty == 2
        assert len(pouw.proofs) == 0
        assert pouw.verified_count == 0
        assert pouw.rejected_count == 0

    def test_create_proof(self):
        """Test creating a proof through PoUW."""
        pouw = ProofOfUsefulWork(difficulty=2)
        proof = pouw.create_proof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100
        )

        assert proof is not None
        assert proof.node_id == "node1"
        assert proof.inference_id == "inf-123"

    def test_submit_valid_proof(self):
        """Test submitting a valid proof."""
        pouw = ProofOfUsefulWork(difficulty=2)
        proof = pouw.create_proof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100
        )

        result = pouw.submit_proof(proof)
        assert result is True
        assert pouw.verified_count == 1
        assert len(pouw.proofs) == 1

    def test_submit_invalid_proof(self):
        """Test submitting an invalid proof."""
        pouw = ProofOfUsefulWork(difficulty=2)
        proof = UsefulWorkProof(
            node_id="node1",
            inference_id="inf-123",
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            energy_mj=-10,  # Invalid
            latency_ms=100,
            timestamp=time.time()
        )

        result = pouw.submit_proof(proof)
        assert result is False
        assert pouw.rejected_count == 1

    def test_select_top_contributor_empty(self):
        """Test selecting top contributor with no proofs."""
        pouw = ProofOfUsefulWork(difficulty=2)
        producer = pouw.select_top_contributor()
        assert producer is None

    def test_select_top_contributor(self):
        """Test selecting top contributor based on work."""
        pouw = ProofOfUsefulWork(difficulty=2)

        # Submit multiple proofs from different nodes
        for i in range(3):
            proof = pouw.create_proof(
                node_id="node1",
                inference_id=f"inf-{i}",
                query_hash=f"query{i}",
                output_hash=f"output{i}",
                model_id="aria-2b-1bit",
                energy_mj=50,
                latency_ms=100
            )
            pouw.submit_proof(proof)

        proof = pouw.create_proof(
            node_id="node2",
            inference_id="inf-x",
            query_hash="queryx",
            output_hash="outputx",
            model_id="aria-2b-1bit",
            energy_mj=50,
            latency_ms=100
        )
        pouw.submit_proof(proof)

        # node1 should be selected (more work)
        producer = pouw.select_top_contributor()
        assert producer == "node1"


class TestSobrietyAttestation:
    """Tests for SobrietyAttestation dataclass."""

    def test_attestation_creation(self):
        """Test creating a sobriety attestation."""
        now = time.time()
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=now - 3600,
            period_end=now,
            total_inferences=100,
            total_energy_mj=5000,
            hardware_type="Intel Core i7",
            os_info="Linux 5.15"
        )
        assert attestation.node_id == "node1"
        assert attestation.total_inferences == 100
        assert attestation.total_energy_mj == 5000

    def test_energy_per_inference(self):
        """Test energy per inference calculation."""
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=0,
            period_end=100,
            total_inferences=100,
            total_energy_mj=5000,
            hardware_type="Intel",
            os_info="Linux"
        )
        assert attestation.energy_per_inference_mj == 50.0

    def test_energy_per_inference_zero_inferences(self):
        """Test energy per inference with zero inferences."""
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=0,
            period_end=100,
            total_inferences=0,
            total_energy_mj=0,
            hardware_type="Intel",
            os_info="Linux"
        )
        assert attestation.energy_per_inference_mj == 0.0

    def test_efficiency_rating_a_plus(self):
        """Test A+ efficiency rating."""
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=0,
            period_end=100,
            total_inferences=100,
            total_energy_mj=2000,  # 20 mJ per inference
            hardware_type="Intel",
            os_info="Linux"
        )
        assert attestation.efficiency_rating == "A+ (Exceptional)"

    def test_efficiency_rating_a(self):
        """Test A efficiency rating."""
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=0,
            period_end=100,
            total_inferences=100,
            total_energy_mj=4000,  # 40 mJ per inference
            hardware_type="Intel",
            os_info="Linux"
        )
        assert attestation.efficiency_rating == "A (Excellent)"

    def test_attestation_to_hash(self):
        """Test attestation hash generation."""
        attestation = SobrietyAttestation(
            node_id="node1",
            period_start=0,
            period_end=100,
            total_inferences=100,
            total_energy_mj=5000,
            hardware_type="Intel",
            os_info="Linux"
        )
        hash1 = attestation.to_hash()
        hash2 = attestation.to_hash()

        assert hash1 == hash2
        assert len(hash1) == 64


class TestProofOfSobriety:
    """Tests for ProofOfSobriety class."""

    def test_pos_creation(self):
        """Test creating a PoS instance."""
        pos = ProofOfSobriety(node_id="node1")
        assert pos.node_id == "node1"
        assert len(pos.attestations) == 0
        assert pos.measurement_start is None

    def test_start_measurement(self):
        """Test starting energy measurement."""
        pos = ProofOfSobriety(node_id="node1")
        pos.start_measurement()

        assert pos.measurement_start is not None
        assert pos.measurement_start > 0

    def test_end_measurement(self):
        """Test ending energy measurement."""
        pos = ProofOfSobriety(node_id="node1")
        pos.start_measurement()

        # Simulate some work
        attestation = pos.end_measurement(inferences_done=10)

        assert attestation is not None
        assert attestation.total_inferences == 10
        assert attestation.node_id == "node1"
        assert len(pos.attestations) == 1

    def test_end_measurement_without_start(self):
        """Test ending measurement without starting raises error."""
        pos = ProofOfSobriety(node_id="node1")

        with pytest.raises(RuntimeError, match="No measurement in progress"):
            pos.end_measurement(inferences_done=10)

    def test_get_network_savings(self):
        """Test calculating network energy savings."""
        pos = ProofOfSobriety(node_id="node1")
        pos.start_measurement()
        pos.end_measurement(inferences_done=100)

        savings = pos.get_network_savings()

        assert "total_inferences" in savings
        assert "aria_energy_mj" in savings
        assert "gpu_equivalent_mj" in savings
        assert "savings_percent" in savings
        assert savings["total_inferences"] == 100

    def test_multiple_measurements(self):
        """Test multiple measurement periods."""
        pos = ProofOfSobriety(node_id="node1")

        for i in range(3):
            pos.start_measurement()
            pos.end_measurement(inferences_done=10)

        assert len(pos.attestations) == 3

        savings = pos.get_network_savings()
        assert savings["total_inferences"] == 30
