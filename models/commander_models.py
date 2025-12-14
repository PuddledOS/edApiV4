from pydantic import BaseModel, Field
from typing import Optional, List


class CommanderRank(BaseModel):
    """Commander rank levels across all categories"""
    timestamp: Optional[str] = None
    combat: int = 0
    trade: int = 0
    explore: int = 0
    soldier: int = 0
    exobiologist: int = 0
    empire: int = 0
    federation: int = 0
    cqc: int = 0


class CommanderProgress(BaseModel):
    """Progress percentages toward next rank (0-100)"""
    timestamp: Optional[str] = None
    combat: int = 0
    trade: int = 0
    explore: int = 0
    soldier: int = 0
    exobiologist: int = 0
    empire: int = 0
    federation: int = 0
    cqc: int = 0


class CommanderReputation(BaseModel):
    """Reputation with major powers"""
    timestamp: Optional[str] = None
    empire: float = 0.0
    federation: float = 0.0
    independent: float = 0.0
    alliance: float = 0.0


class CommanderStatus(BaseModel):
    """Complete commander status including rank, progress, and reputation"""
    timestamp: Optional[str] = None
    rank: Optional[CommanderRank] = None
    progress: Optional[CommanderProgress] = None
    reputation: Optional[CommanderReputation] = None


class RankHistory(BaseModel):
    """Historical rank progression"""
    total_events: int = 0
    earliest_timestamp: Optional[str] = None
    latest_timestamp: Optional[str] = None
    current_rank: Optional[CommanderRank] = None
    history: List[CommanderRank] = Field(default_factory=list)


class ProgressHistory(BaseModel):
    """Historical progress tracking"""
    total_events: int = 0
    earliest_timestamp: Optional[str] = None
    latest_timestamp: Optional[str] = None
    current_progress: Optional[CommanderProgress] = None
    history: List[CommanderProgress] = Field(default_factory=list)


class ReputationHistory(BaseModel):
    """Historical reputation tracking"""
    total_events: int = 0
    earliest_timestamp: Optional[str] = None
    latest_timestamp: Optional[str] = None
    current_reputation: Optional[CommanderReputation] = None
    history: List[CommanderReputation] = Field(default_factory=list)