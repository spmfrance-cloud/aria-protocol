"""Tests for the ARIA consent module."""

import pytest
from datetime import datetime
from aria.consent import ARIAConsent, TaskType


class TestTaskType:
    """Tests for TaskType enum."""

    def test_task_type_values(self):
        """Test that all expected task types exist."""
        assert TaskType.TEXT_GENERATION is not None
        assert TaskType.CODE_GENERATION is not None
        assert TaskType.SUMMARIZATION is not None
        assert TaskType.TRANSLATION is not None
        assert TaskType.EMBEDDING is not None
        assert TaskType.ANY is not None

    def test_task_type_iteration(self):
        """Test that TaskType can be iterated."""
        task_types = list(TaskType)
        assert len(task_types) == 6


class TestARIAConsent:
    """Tests for ARIAConsent class."""

    def test_default_consent_creation(self):
        """Test creating consent with default values."""
        consent = ARIAConsent()
        assert consent.cpu_percent == 25
        assert consent.max_ram_mb == 512
        assert consent.max_bandwidth_mbps == 10.0
        assert consent.max_concurrent_tasks == 2
        assert consent.allow_logging is True
        assert consent.allow_geo_tracking is False
        assert consent.version == "1.0"

    def test_custom_consent_creation(self):
        """Test creating consent with custom values."""
        consent = ARIAConsent(
            cpu_percent=50,
            max_ram_mb=1024,
            max_bandwidth_mbps=20.0,
            schedule="09:00-18:00",
            task_types=[TaskType.TEXT_GENERATION, TaskType.CODE_GENERATION],
            max_concurrent_tasks=4,
            allow_logging=False,
            min_reward_per_inference=0.01,
            node_id="test-node"
        )
        assert consent.cpu_percent == 50
        assert consent.max_ram_mb == 1024
        assert consent.max_bandwidth_mbps == 20.0
        assert consent.schedule == "09:00-18:00"
        assert len(consent.task_types) == 2
        assert consent.max_concurrent_tasks == 4
        assert consent.allow_logging is False
        assert consent.min_reward_per_inference == 0.01
        assert consent.node_id == "test-node"

    def test_accepts_task_any(self):
        """Test that consent with ANY task type accepts all tasks."""
        consent = ARIAConsent(task_types=[TaskType.ANY])
        assert consent.accepts_task(TaskType.TEXT_GENERATION) is True
        assert consent.accepts_task(TaskType.CODE_GENERATION) is True
        assert consent.accepts_task(TaskType.SUMMARIZATION) is True

    def test_accepts_task_specific(self):
        """Test that consent with specific task types only accepts those."""
        consent = ARIAConsent(task_types=[TaskType.TEXT_GENERATION])
        assert consent.accepts_task(TaskType.TEXT_GENERATION) is True
        assert consent.accepts_task(TaskType.CODE_GENERATION) is False

    def test_to_hash(self):
        """Test that consent hash is consistent."""
        consent = ARIAConsent(cpu_percent=25, max_ram_mb=512)
        hash1 = consent.to_hash()
        hash2 = consent.to_hash()
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars

    def test_to_dict(self):
        """Test consent serialization to dict."""
        consent = ARIAConsent(
            cpu_percent=30,
            max_ram_mb=256,
            task_types=[TaskType.TEXT_GENERATION]
        )
        data = consent.to_dict()
        assert data["cpu_percent"] == 30
        assert data["max_ram_mb"] == 256
        assert "task_types" in data
        assert data["version"] == "1.0"

    def test_from_dict(self):
        """Test consent deserialization from dict."""
        original = ARIAConsent(
            cpu_percent=40,
            max_ram_mb=768,
            task_types=[TaskType.SUMMARIZATION],
            node_id="test-123"
        )
        data = original.to_dict()
        restored = ARIAConsent.from_dict(data)

        assert restored.cpu_percent == original.cpu_percent
        assert restored.max_ram_mb == original.max_ram_mb
        assert restored.node_id == original.node_id

    def test_matches_request_valid(self):
        """Test that valid requests match consent."""
        consent = ARIAConsent(
            max_ram_mb=512,
            task_types=[TaskType.TEXT_GENERATION],
            min_reward_per_inference=0.001
        )
        request = {
            "ram_mb": 256,
            "task_type": TaskType.TEXT_GENERATION,
            "reward": 0.01
        }
        assert consent.matches_request(request) is True

    def test_matches_request_insufficient_reward(self):
        """Test that requests with insufficient reward don't match."""
        consent = ARIAConsent(min_reward_per_inference=0.1)
        request = {
            "ram_mb": 256,
            "task_type": TaskType.TEXT_GENERATION,
            "reward": 0.01
        }
        assert consent.matches_request(request) is False

    def test_matches_request_wrong_task_type(self):
        """Test that requests with wrong task type don't match."""
        consent = ARIAConsent(task_types=[TaskType.TEXT_GENERATION])
        request = {
            "ram_mb": 256,
            "task_type": TaskType.CODE_GENERATION,
            "reward": 0.01
        }
        assert consent.matches_request(request) is False

    def test_is_available_now_full_day(self):
        """Test availability with 24-hour schedule."""
        consent = ARIAConsent(schedule="00:00-23:59")
        # Should always be available with full day schedule
        assert consent.is_available_now() is True

    def test_consent_hash_uniqueness(self):
        """Test that different consents produce different hashes."""
        consent1 = ARIAConsent(cpu_percent=25)
        consent2 = ARIAConsent(cpu_percent=50)
        assert consent1.to_hash() != consent2.to_hash()
