import os
import sys
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Add project root to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import SessionLocal
from database.models import User, Ticket, Comment, KnowledgeBase

# Initialize FastMCP Server
mcp = FastMCP("Ticket System")

# Helper to format datetime in JSON serialize
def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

@mcp.tool(description="List all support tickets in the system.")
def list_tickets() -> str:
    """Return all tickets in the system as a JSON string."""
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
        result = []
        for t in tickets:
            result.append({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "created_by_user": t.creator.username if t.creator else "Unknown"
            })
        return json.dumps(result, default=datetime_handler, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to list tickets: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Get detailed information about a support ticket including its comments.")
def get_ticket(ticket_id: int) -> str:
    """Return details and comments for a specific ticket_id as a JSON string."""
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found."})
        
        comments_list = []
        for c in t.comments:
            comments_list.append({
                "id": c.id,
                "comment": c.comment,
                "author": c.author,
                "created_at": c.created_at
            })
            
        ticket_detail = {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
            "created_by_user": t.creator.username if t.creator else "Unknown",
            "comments": comments_list
        }
        return json.dumps(ticket_detail, default=datetime_handler, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get ticket: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Create a new support ticket. Priority should be LOW, MEDIUM, HIGH, or CRITICAL.")
def create_ticket(title: str, description: str, priority: str = "LOW") -> str:
    """Create a new support ticket and return the created ticket's info as a JSON string."""
    db = SessionLocal()
    try:
        # Resolve mcp_user or fall back to any admin user
        mcp_user = db.query(User).filter(User.username == "mcp_user").first()
        if not mcp_user:
            mcp_user = db.query(User).filter(User.role == "Admin").first()
        if not mcp_user:
            return json.dumps({"error": "No valid user context found to attribute ticket creation."})
            
        valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        priority_upper = priority.upper()
        if priority_upper not in valid_priorities:
            priority_upper = "LOW"
            
        new_ticket = Ticket(
            title=title,
            description=description,
            priority=priority_upper,
            status="OPEN",
            created_by=mcp_user.id
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        return json.dumps({
            "message": "Ticket created successfully",
            "ticket": {
                "id": new_ticket.id,
                "title": new_ticket.title,
                "description": new_ticket.description,
                "status": new_ticket.status,
                "priority": new_ticket.priority,
                "created_at": new_ticket.created_at,
                "created_by": mcp_user.username
            }
        }, default=datetime_handler, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Failed to create ticket: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Add a comment to an existing support ticket.")
def add_comment(ticket_id: int, comment: str) -> str:
    """Add a comment from mcp_user to a ticket and return the result as a JSON string."""
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found."})
            
        new_comment = Comment(
            ticket_id=ticket_id,
            comment=comment,
            author="mcp_user"
        )
        db.add(new_comment)
        
        # If ticket was OPEN, transition it to IN_PROGRESS when commented on by MCP
        if ticket.status == "OPEN":
            ticket.status = "IN_PROGRESS"
            ticket.updated_at = datetime.utcnow()
            
        db.commit()
        db.refresh(new_comment)
        
        return json.dumps({
            "message": "Comment added successfully",
            "comment": {
                "id": new_comment.id,
                "ticket_id": new_comment.ticket_id,
                "comment": new_comment.comment,
                "author": new_comment.author,
                "created_at": new_comment.created_at
            }
        }, default=datetime_handler, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Failed to add comment: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Search the Help Desk Knowledge Base for questions, answers, or categories.")
def search_kb(query: str) -> str:
    """Search the Knowledge Base and return matching articles as a JSON string."""
    db = SessionLocal()
    try:
        search_pattern = f"%{query}%"
        results = db.query(KnowledgeBase).filter(
            (KnowledgeBase.question.like(search_pattern)) |
            (KnowledgeBase.answer.like(search_pattern)) |
            (KnowledgeBase.category.like(search_pattern))
        ).all()
        
        articles = []
        for r in results:
            articles.append({
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "category": r.category
            })
            
        return json.dumps(articles, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search Knowledge Base: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Update fields on an existing support ticket. You can update title, description, status (OPEN, IN_PROGRESS, RESOLVED, CLOSED), or priority (LOW, MEDIUM, HIGH, CRITICAL). Only provide the fields that need updating.")
def update_ticket(
    ticket_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None
) -> str:
    """Update fields on an existing support ticket in the database."""
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found."})

        updated = {}
        if title is not None:
            t.title = title
            updated["title"] = title
        if description is not None:
            t.description = description
            updated["description"] = description
        if status is not None:
            status_upper = status.upper()
            valid_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
            if status_upper in valid_statuses:
                t.status = status_upper
                updated["status"] = status_upper
            else:
                return json.dumps({"error": f"Invalid status: {status}. Must be one of {valid_statuses}."})
        if priority is not None:
            priority_upper = priority.upper()
            valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if priority_upper in valid_priorities:
                t.priority = priority_upper
                updated["priority"] = priority_upper
            else:
                return json.dumps({"error": f"Invalid priority: {priority}. Must be one of {valid_priorities}."})

        if updated:
            t.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(t)

        return json.dumps({
            "message": f"Ticket #{ticket_id} updated successfully.",
            "updated_fields": updated,
            "ticket": {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "updated_at": t.updated_at
            }
        }, default=datetime_handler, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Failed to update ticket: {str(e)}"})
    finally:
        db.close()

@mcp.tool(description="Permanently delete a ticket from the system. For audit compliance, the ticket MUST be in CLOSED or RESOLVED status before deletion is allowed.")
def delete_ticket(ticket_id: int) -> str:
    """Delete a ticket from the database if its status is CLOSED or RESOLVED."""
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found."})

        # Enforce status restriction
        if t.status not in ["CLOSED", "RESOLVED"]:
            return json.dumps({
                "error": f"Ticket #{ticket_id} cannot be deleted. Current status is {t.status}. A ticket must be RESOLVED or CLOSED before it can be deleted."
            })

        db.delete(t)
        db.commit()
        return json.dumps({
            "message": f"Ticket #{ticket_id} has been permanently deleted from the database.",
            "deleted_ticket_id": ticket_id
        }, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Failed to delete ticket: {str(e)}"})
    finally:
        db.close()

if __name__ == "__main__":
    # Start the FastMCP server on standard I/O (stdio)
    mcp.run()
