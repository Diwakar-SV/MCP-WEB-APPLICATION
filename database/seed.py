import os
import sys

# Add root folder to path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy.orm import Session
import bcrypt
from database.db import engine, Base, SessionLocal
from database.models import User, Ticket, Comment, KnowledgeBase

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def seed_db():
    print("Re-creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("Creating users...")
        admin = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            role="Admin"
        )
        user = User(
            username="user",
            email="user@example.com",
            password=hash_password("user123"),
            role="User"
        )
        mcp_user = User(
            username="mcp_user",
            email="mcp_user@example.com",
            password=hash_password("mcp_pass_secure_123!"),
            role="Admin"  # MCP server needs admin permissions or high authorization
        )
        db.add_all([admin, user, mcp_user])
        db.commit()
        db.refresh(admin)
        db.refresh(user)
        db.refresh(mcp_user)

        print("Creating Knowledge Base articles...")
        kb_articles = [
            KnowledgeBase(
                question="How do I reset my company password?",
                answer="Go to https://identity.company.com, click 'Forgot Password', and complete the multi-factor authentication (MFA) verification via Duo to set a new password.",
                category="IT Support"
            ),
            KnowledgeBase(
                question="How do I connect to the company VPN?",
                answer="Download and install Cisco AnyConnect. Configure the gateway address to 'vpn.company.com'. Enter your email credentials and approve the push notification on your Duo mobile app.",
                category="IT Support"
            ),
            KnowledgeBase(
                question="What is the standard procedure for expense reimbursement?",
                answer="Submit all travel and hardware receipts through the Expensify portal. Submissions must be sent before the 25th of the month. Ensure you link each expense to a specific client or department project code.",
                category="HR & Finance"
            ),
            KnowledgeBase(
                question="How do I request a software license (e.g. IntelliJ, Copilot)?",
                answer="Open a ticket category 'Software Request' containing the software name, business justification, and manager approval email screenshot. The IT team will provision it within 24-48 hours.",
                category="Engineering"
            ),
            KnowledgeBase(
                question="Where can I find the holiday calendar?",
                answer="The official holiday calendar is hosted on our Wiki page under HR Policies -> Calendars. It details all 12 public holidays recognized by the company.",
                category="HR & Finance"
            )
        ]
        db.add_all(kb_articles)
        db.commit()

        print("Creating tickets and comments...")
        # Ticket 1
        t1 = Ticket(
            title="Unable to access AWS Console staging environment",
            description="I get an AccessDenied error when attempting to assume the developer role in the staging account. I need this to deploy my microservice test branch.",
            status="IN_PROGRESS",
            priority="HIGH",
            created_by=user.id
        )
        db.add(t1)
        db.commit()
        db.refresh(t1)

        c1 = Comment(
            ticket_id=t1.id,
            comment="I checked your AWS permissions group. Your account was missing the staging developer policy attachment. I've added it now. Please try again in 5 minutes.",
            author=admin.username
        )
        db.add(c1)

        # Ticket 2
        t2 = Ticket(
            title="Broken office chair in Desk 42",
            description="The hydraulic lift in my desk chair is broken, making it sink to the floor. I need a replacement office chair when possible.",
            status="OPEN",
            priority="LOW",
            created_by=user.id
        )
        db.add(t2)

        # Ticket 3
        t3 = Ticket(
            title="Production Postgres slow query warnings",
            description="Our query latency has spiked to over 2.5 seconds on the user lookup endpoint. We are seeing transaction locks. High risk of outage.",
            status="OPEN",
            priority="CRITICAL",
            created_by=admin.id
        )
        db.add(t3)
        db.commit()
        db.refresh(t3)

        c2 = Comment(
            ticket_id=t3.id,
            comment="Running EXPLAIN ANALYZE shows a missing index on the 'users.email' column. I will prepare a migration script to build the index concurrently.",
            author=admin.username
        )
        db.add(c2)

        # Ticket 4
        t4 = Ticket(
            title="Request for GitHub Copilot access",
            description="Requesting Copilot access for writing frontend components. Manager approved this in Slack.",
            status="RESOLVED",
            priority="MEDIUM",
            created_by=user.id
        )
        db.add(t4)
        db.commit()
        db.refresh(t4)

        c3 = Comment(
            ticket_id=t4.id,
            comment="Seat assigned. You should receive a GitHub invitation in your inbox shortly.",
            author=admin.username
        )
        db.add(c3)

        db.commit()
        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
