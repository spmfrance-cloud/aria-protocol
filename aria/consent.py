"""
ARIA Protocol - Consent Contract
Defines how each node consents to contribute resources.
Every node explicitly declares what it is willing to give.

MIT License - Anthony MURGO, 2026
"""

import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class TaskType(Enum):
    """Types of inference tasks a node can accept."""
    TEXT_GENERATION = "text_gen"
    CODE_GENERATION = "code_gen"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    EMBEDDING = "embedding"
    ANY = "any"


@dataclass
class ARIAConsent:
    """
    A consent descriptor that defines exactly what resources
    a node is willing to contribute to the ARIA network.
    
    This is the ethical backbone of the protocol. No work is
    assigned to a node unless it matches the consent parameters.
    
    Example:
        consent = ARIAConsent(
            cpu_percent=25,
            schedule="08:00-22:00",
            task_types=[TaskType.TEXT_GENERATION],
            max_bandwidth_mbps=10,
            max_ram_mb=512
        )
    """
    
    # Resource limits
    cpu_percent: int = 25           # Max CPU usage (1-100)
    max_ram_mb: int = 512           # Max RAM allocation in MB
    max_bandwidth_mbps: float = 10  # Max network bandwidth
    
    # Availability
    schedule: str = "00:00-23:59"   # Available hours (UTC)
    days: List[str] = field(default_factory=lambda: [
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
    ])
    
    # Task preferences
    task_types: List[TaskType] = field(default_factory=lambda: [TaskType.ANY])
    max_concurrent_tasks: int = 2
    
    # Privacy
    allow_logging: bool = True       # Allow inference metadata logging
    allow_geo_tracking: bool = False # Allow geographic location tracking
    
    # Economics
    min_reward_per_inference: float = 0.0  # Minimum ARIA tokens per task
    
    # Metadata
    version: str = "1.0"
    created_at: float = field(default_factory=time.time)
    node_id: Optional[str] = None
    
    def is_available_now(self) -> bool:
        """Check if the node is available based on schedule."""
        now = time.gmtime()
        
        # Check day
        day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        current_day = day_names[now.tm_wday]
        if current_day not in self.days:
            return False
        
        # Check time
        start_str, end_str = self.schedule.split("-")
        start_h, start_m = map(int, start_str.split(":"))
        end_h, end_m = map(int, end_str.split(":"))
        
        current_minutes = now.tm_hour * 60 + now.tm_min
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        if end_minutes > start_minutes:
            return start_minutes <= current_minutes <= end_minutes
        else:  # Overnight schedule (e.g., 22:00-06:00)
            return current_minutes >= start_minutes or current_minutes <= end_minutes
    
    def accepts_task(self, task_type: TaskType) -> bool:
        """Check if this consent allows a given task type."""
        if TaskType.ANY in self.task_types:
            return True
        return task_type in self.task_types
    
    def matches_request(self, request: dict) -> bool:
        """
        Check if an inference request matches this consent.
        Returns True only if ALL consent conditions are met.
        """
        if not self.is_available_now():
            return False
        
        task_type = request.get("task_type", TaskType.ANY)
        if not self.accepts_task(task_type):
            return False
        
        ram_needed = request.get("ram_mb", 0)
        if ram_needed > self.max_ram_mb:
            return False
        
        reward = request.get("reward", 0)
        if reward < self.min_reward_per_inference:
            return False
        
        return True
    
    def to_hash(self) -> str:
        """Generate a unique hash of this consent for on-chain registration."""
        data = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """Serialize for network transmission."""
        d = asdict(self)
        d["task_types"] = [t.value for t in self.task_types]
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "ARIAConsent":
        """Deserialize from network data."""
        data["task_types"] = [TaskType(t) for t in data.get("task_types", ["any"])]
        return cls(**data)
    
    def __repr__(self) -> str:
        return (
            f"ARIAConsent(cpu={self.cpu_percent}%, ram={self.max_ram_mb}MB, "
            f"schedule={self.schedule}, tasks={[t.value for t in self.task_types]})"
        )
