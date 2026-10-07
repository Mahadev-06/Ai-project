from enum import Enum

class ClaimOutcome(str, Enum):
    supported = "supported"
    contradicted = "contradicted"
    conflicting = "conflicting"
    insufficient = "insufficient"
    not_checkable = "not_checkable"

class AnalysisStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    partial = "partial"
    failed = "failed"
    cancelled = "cancelled"

class EvidenceMode(str, Enum):
    local = "local"
    live = "live"
    auto = "auto"

class EvidenceStance(str, Enum):
    supports = "supports"
    contradicts = "contradicts"
    neutral = "neutral"

class ProvenanceCategory(str, Enum):
    documented = "documented"
    partially_documented = "partially_documented"
    unknown = "unknown"
