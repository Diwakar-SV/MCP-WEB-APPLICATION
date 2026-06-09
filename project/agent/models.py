from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ExecutionStep(BaseModel):
    """Represents a single step in the ReAct (Reasoning + Action) execution loop."""
    step_number: int
    thought: str
    action: str
    observation: str
    timestamp: str = datetime.utcnow().isoformat()

class AgentState(BaseModel):
    """Tracks the overall execution state of the support agent workflow."""
    issue_text: str
    priority: str = "LOW"
    kb_results: List[Any] = []
    matching_tickets: List[Any] = []
    is_duplicate: bool = False
    duplicate_ticket_id: Optional[int] = None
    created_ticket_id: Optional[int] = None
    added_comment_id: Optional[int] = None
    history: List[ExecutionStep] = []
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    final_response: Optional[str] = None

class WorkflowResult(BaseModel):
    """The final outcome of the agent workflow returned to clients and APIs."""
    success: bool
    final_response: str
    steps: List[ExecutionStep]
    state: dict
