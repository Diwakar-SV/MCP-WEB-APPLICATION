import os
import sys
from datetime import datetime
from typing import List, Optional

# Add project root to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from database.db import get_db
from database.models import User as UserModel, Ticket as TicketModel, Comment as CommentModel, KnowledgeBase as KBModel
from backend.auth import verify_password, create_access_token, get_current_user, get_admin_user, get_password_hash
from backend.schemas import (
    LoginRequest, LoginResponse, UserResponse,
    TicketCreate, TicketUpdate, TicketResponse,
    CommentCreate, CommentResponse, KnowledgeBaseResponse,
    DashboardStats, StatusCount, DayCount
)

app = FastAPI(title="Help Desk Ticket Management System API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION ---
@app.post("/login", response_model=LoginResponse)
@app.post("/api/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# --- TICKETS ---
@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    db_ticket = TicketModel(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.upper(),
        status="OPEN",
        created_by=current_user.id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets", response_model=List[TicketResponse])
@app.get("/api/tickets", response_model=List[TicketResponse])
def get_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TicketModel)
    
    # Scoping: regular users only see their own tickets, admins see everything
    if current_user.role != "Admin":
        query = query.filter(TicketModel.created_by == current_user.id)
        
    if status:
        query = query.filter(TicketModel.status == status.upper())
    if priority:
        query = query.filter(TicketModel.priority == priority.upper())
    if search:
        query = query.filter(
            or_(
                TicketModel.title.icontains(search),
                TicketModel.description.icontains(search),
                TicketModel.id.like(f"%{search}%")
            )
        )
        
    # Order by created_at desc (newest first)
    query = query.order_by(TicketModel.created_at.desc())
    
    # Return paginated results
    return query.offset(skip).limit(limit).all()

@app.get("/tickets/{id}", response_model=TicketResponse)
@app.get("/api/tickets/{id}", response_model=TicketResponse)
def get_ticket(id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    db_ticket = db.query(TicketModel).filter(TicketModel.id == id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Check permissions: user can only see their own, admin can see all
    if current_user.role != "Admin" and db_ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to view this ticket")
        
    return db_ticket

@app.put("/tickets/{id}", response_model=TicketResponse)
@app.put("/api/tickets/{id}", response_model=TicketResponse)
def update_ticket(id: int, ticket_update: TicketUpdate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    db_ticket = db.query(TicketModel).filter(TicketModel.id == id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Check permissions
    is_admin = current_user.role == "Admin"
    is_owner = db_ticket.created_by == current_user.id
    
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to update this ticket")
        
    # Apply updates
    update_data = ticket_update.dict(exclude_unset=True)
    
    # Non-admins can only change status (e.g. to CLOSE their ticket)
    if not is_admin:
        if "title" in update_data: del update_data["title"]
        if "description" in update_data: del update_data["description"]
        if "priority" in update_data: del update_data["priority"]
        
    for key, value in update_data.items():
        if key == "status" or key == "priority":
            setattr(db_ticket, key, value.upper())
        else:
            setattr(db_ticket, key, value)
            
    db_ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.delete("/tickets/{id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/api/tickets/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(id: int, current_user: UserModel = Depends(get_admin_user), db: Session = Depends(get_db)):
    db_ticket = db.query(TicketModel).filter(TicketModel.id == id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db.delete(db_ticket)
    db.commit()
    return None

# --- COMMENTS ---
@app.post("/tickets/{id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/tickets/{id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(id: int, comment: CommentCreate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    db_ticket = db.query(TicketModel).filter(TicketModel.id == id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # User can only comment on their own ticket, Admin on any
    if current_user.role != "Admin" and db_ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot comment on this ticket")
        
    db_comment = CommentModel(
        ticket_id=id,
        comment=comment.comment,
        author=current_user.username
    )
    db.add(db_comment)
    
    # Auto transition ticket to IN_PROGRESS if commented by admin and currently OPEN
    if current_user.role == "Admin" and db_ticket.status == "OPEN":
        db_ticket.status = "IN_PROGRESS"
        db_ticket.updated_at = datetime.utcnow()
        
    db.commit()
    db.refresh(db_comment)
    return db_comment

# --- KNOWLEDGE BASE ---
@app.get("/kb/search", response_model=List[KnowledgeBaseResponse])
@app.get("/api/kb/search", response_model=List[KnowledgeBaseResponse])
def search_kb(query: Optional[str] = None, db: Session = Depends(get_db)):
    if not query:
        return db.query(KBModel).all()
        
    search_pattern = f"%{query}%"
    results = db.query(KBModel).filter(
        or_(
            KBModel.question.like(search_pattern),
            KBModel.answer.like(search_pattern),
            KBModel.category.like(search_pattern)
        )
    ).all()
    return results

# --- DASHBOARD STATS ---
@app.get("/dashboard/stats", response_model=DashboardStats)
@app.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    tickets_query = db.query(TicketModel)
    
    # User scoping
    if current_user.role != "Admin":
        tickets_query = tickets_query.filter(TicketModel.created_by == current_user.id)
        
    tickets = tickets_query.all()
    
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t.status == "OPEN"])
    resolved_tickets = len([t for t in tickets if t.status == "RESOLVED" or t.status == "CLOSED"])
    high_priority_tickets = len([t for t in tickets if t.priority in ["HIGH", "CRITICAL"]])
    
    # Status distribution
    status_map = {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0, "CLOSED": 0}
    for t in tickets:
        status_map[t.status] = status_map.get(t.status, 0) + 1
        
    status_distribution = [
        StatusCount(status=k, count=v) for k, v in status_map.items()
    ]
    
    # Tickets per day grouping
    # Group by date part of created_at (YYYY-MM-DD)
    date_map = {}
    for t in tickets:
        date_str = t.created_at.strftime("%Y-%m-%d")
        date_map[date_str] = date_map.get(date_str, 0) + 1
        
    # Sort dates chronologically
    sorted_dates = sorted(date_map.keys())
    tickets_per_day = [
        DayCount(date=d, count=date_map[d]) for d in sorted_dates
    ]
    
    # If empty tickets per day, return today with 0
    if not tickets_per_day:
        tickets_per_day = [DayCount(date=datetime.utcnow().strftime("%Y-%m-%d"), count=0)]
        
    return DashboardStats(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        high_priority_tickets=high_priority_tickets,
        status_distribution=status_distribution,
        tickets_per_day=tickets_per_day
    )
