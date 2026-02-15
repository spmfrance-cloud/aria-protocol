"""Tests for the ARIA ledger module."""

import time
from aria.ledger import InferenceRecord, Block, ProvenanceLedger


class TestInferenceRecord:
    """Tests for InferenceRecord dataclass."""

    def test_record_creation(self):
        """Test creating an inference record."""
        record = InferenceRecord(
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            node_ids=["node1", "node2"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=25
        )
        assert record.query_hash == "abc123"
        assert record.output_hash == "def456"
        assert record.model_id == "aria-2b-1bit"
        assert len(record.node_ids) == 2
        assert record.energy_mj == 50
        assert record.latency_ms == 100
        assert record.tokens_generated == 25

    def test_record_to_hash(self):
        """Test that record hash is consistent."""
        record = InferenceRecord(
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=1000.0,
            tokens_generated=25
        )
        hash1 = record.to_hash()
        hash2 = record.to_hash()
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256

    def test_record_hash_uniqueness(self):
        """Test that different records produce different hashes."""
        record1 = InferenceRecord(
            query_hash="abc123",
            output_hash="def456",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=1000.0,
            tokens_generated=25
        )
        record2 = InferenceRecord(
            query_hash="xyz789",
            output_hash="def456",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=1000.0,
            tokens_generated=25
        )
        assert record1.to_hash() != record2.to_hash()


class TestBlock:
    """Tests for Block dataclass."""

    def test_block_creation(self):
        """Test creating a block."""
        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        block = Block(
            index=1,
            timestamp=time.time(),
            records=[record],
            previous_hash="0" * 64
        )
        assert block.index == 1
        assert len(block.records) == 1
        assert block.previous_hash == "0" * 64

    def test_block_compute_hash(self):
        """Test that block hash is computed correctly."""
        block = Block(
            index=0,
            timestamp=1000.0,
            records=[],
            previous_hash="0" * 64
        )
        hash1 = block.compute_hash()
        hash2 = block.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_block_seal(self):
        """Test sealing a block."""
        block = Block(
            index=1,
            timestamp=time.time(),
            records=[],
            previous_hash="0" * 64
        )
        sealed_hash = block.seal(difficulty=1)
        assert sealed_hash.startswith("0")
        assert block.hash == sealed_hash


class TestProvenanceLedger:
    """Tests for ProvenanceLedger class."""

    def test_ledger_creation(self):
        """Test creating a ledger with genesis block."""
        ledger = ProvenanceLedger(difficulty=1)
        assert len(ledger.chain) == 1
        assert ledger.last_block.index == 0
        assert ledger.last_block.previous_hash == "0" * 64

    def test_add_record(self):
        """Test adding a record to pending pool."""
        ledger = ProvenanceLedger(difficulty=1)
        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        record_hash = ledger.add_record(record)
        assert len(ledger.pending_records) == 1
        assert record_hash == record.to_hash()

    def test_seal_pending_block(self):
        """Test sealing a block with pending records."""
        ledger = ProvenanceLedger(difficulty=1)

        # Add a record
        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        ledger.add_record(record)

        # Seal block
        block = ledger.seal_pending_block(contributor_id="contributor1")
        assert block is not None
        assert block.index == 1
        assert block.contributor_id == "contributor1"
        assert len(ledger.chain) == 2
        assert len(ledger.pending_records) == 0

    def test_seal_empty_pending(self):
        """Test that sealing with no pending records returns None."""
        ledger = ProvenanceLedger(difficulty=1)
        block = ledger.seal_pending_block(contributor_id="contributor1")
        assert block is None

    def test_verify_chain(self):
        """Test ledger chain verification."""
        ledger = ProvenanceLedger(difficulty=1)

        # Add and seal a record
        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        ledger.add_record(record)
        ledger.seal_pending_block(contributor_id="contributor1")

        assert ledger.verify_chain() is True

    def test_get_record_by_hash(self):
        """Test retrieving a record by its hash."""
        ledger = ProvenanceLedger(difficulty=1)

        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        record_hash = ledger.add_record(record)
        ledger.seal_pending_block(contributor_id="contributor1")

        retrieved = ledger.get_record_by_hash(record_hash)
        assert retrieved is not None
        assert retrieved.query_hash == "abc"

    def test_get_records_by_node(self):
        """Test retrieving records by node ID."""
        ledger = ProvenanceLedger(difficulty=1)

        record1 = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        record2 = InferenceRecord(
            query_hash="xyz",
            output_hash="uvw",
            model_id="aria-2b-1bit",
            node_ids=["node2"],
            energy_mj=60,
            latency_ms=110,
            timestamp=time.time(),
            tokens_generated=15
        )
        ledger.add_record(record1)
        ledger.add_record(record2)
        ledger.seal_pending_block(contributor_id="contributor1")

        node1_records = ledger.get_records_by_node("node1")
        assert len(node1_records) == 1
        assert node1_records[0].query_hash == "abc"

    def test_get_records_by_model(self):
        """Test retrieving records by model ID."""
        ledger = ProvenanceLedger(difficulty=1)

        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        ledger.add_record(record)
        ledger.seal_pending_block(contributor_id="contributor1")

        model_records = ledger.get_records_by_model("aria-2b-1bit")
        assert len(model_records) == 1

    def test_get_network_stats(self):
        """Test getting network statistics."""
        ledger = ProvenanceLedger(difficulty=1)

        record = InferenceRecord(
            query_hash="abc",
            output_hash="def",
            model_id="aria-2b-1bit",
            node_ids=["node1"],
            energy_mj=50,
            latency_ms=100,
            timestamp=time.time(),
            tokens_generated=10
        )
        ledger.add_record(record)
        ledger.seal_pending_block(contributor_id="contributor1")

        stats = ledger.get_network_stats()
        assert "total_inferences" in stats
        assert "total_energy_joules" in stats
        assert stats["total_inferences"] == 1
        assert stats["total_energy_joules"] == 0.05  # 50 mJ = 0.05 J

    def test_export_chain(self):
        """Test exporting ledger chain as JSON."""
        ledger = ProvenanceLedger(difficulty=1)

        exported = ledger.export_chain()
        assert isinstance(exported, str)
        # The export is a JSON array of blocks
        import json
        data = json.loads(exported)
        assert isinstance(data, list)
        assert len(data) >= 1  # At least genesis block
