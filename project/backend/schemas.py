from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- COMMENT SCHEMAS ---
class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1)

class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    comment: str
    author: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- TICKET SCHEMAS ---
class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5)
    priority: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None      # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority: Optional[str] = None    # LOW, MEDIUM, HIGH, CRITICAL

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    created_by: int
    creator: UserResponse
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True

# --- KNOWLEDGE BASE SCHEMAS ---
class KnowledgeBaseResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str

    class Config:
        from_attributes = True

# --- DASHBOARD STATS ---
class StatusCount(BaseModel):
    status: str
    count: int

class DayCount(BaseModel):
    date: str
    count: int

class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    high_priority_tickets: int
    status_distribution: List[StatusCount]
    tickets_per_day: List[DayCount]

# --- AGENT SCHEMAS ---
class AgentRunRequest(BaseModel):
    issue: str = Field(..., min_length=5)

class ExecutionStepSchema(BaseModel):
    step_number: int
    thought: str
    action: str
    observation: str
    timestamp: str

class AgentRunResponse(BaseModel):
    success: bool
    final_response: str
    steps: List[ExecutionStepSchema]
    state: Dict[str, Any]

