from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Use Pydantic for JSON serialization
class DraftVersion(BaseModel):
    version_num: int
    content: str
    created_at: datetime
    created_by: str
    notes: str = ""

class SafetyFlag(BaseModel):
    line_num: int
    severity: str  # "critical", "moderate", "low"
    issue: str
    suggestion: str
    resolved: bool = False

class CerinasState(BaseModel):
    # Input
    user_intent: str
    original_query: str
    
    # Drafting
    current_draft: str = ""
    draft_history: List[DraftVersion] = Field(default_factory=list)
    
    # Safety Review
    safety_flags: List[SafetyFlag] = Field(default_factory=list)
    safety_score: float = 0.0
    
    # Clinical Review
    clinical_feedback: str = ""
    empathy_score: float = 0.0
    tone_issues: List[str] = Field(default_factory=list)
    
    # Metadata
    iteration_count: int = 0
    max_iterations: int = 3
    status: str = "drafting"
    halted_for_human: bool = False
    human_approval: bool = False
    human_edits: str = ""
    
    # Audit trail
    agent_notes: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Final result
    final_protocol: str = ""
