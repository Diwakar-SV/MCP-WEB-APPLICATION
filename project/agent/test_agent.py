import os
import sys
import json
import unittest

# Add project root to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import SessionLocal
from database.models import Ticket, Comment
from agent.planner import classify_priority, is_duplicate_ticket
from agent.executor import Executor
from agent.workflow import HelpdeskAgentWorkflow

class TestHelpdeskAgent(unittest.TestCase):
    
    def setUp(self):
        # We use the existing local tickets.db for testing.
        # Ensure database is accessible
        self.db = SessionLocal()
        
    def tearDown(self):
        self.db.close()
        
    def test_priority_classifier(self):
        """Verify that issues are correctly classified by priority."""
        self.assertEqual(classify_priority("Database outage in production environment"), "CRITICAL")
        self.assertEqual(classify_priority("Security breach detected on server 4"), "HIGH")
        self.assertEqual(classify_priority("FastAPI application error slow query warning"), "MEDIUM")
        self.assertEqual(classify_priority("Where is the holiday calendar?"), "LOW")
        self.assertEqual(classify_priority("Need a new developer laptop request"), "LOW")

    def test_jaccard_similarity_duplicate_check(self):
        """Verify duplicate ticket detection using word similarity."""
        mock_tickets = [
            {"id": 1, "title": "Unable to access AWS Console staging", "description": "Access denied errors", "status": "IN_PROGRESS"},
            {"id": 2, "title": "Broken office chair at Desk 42", "description": "Hydraulic lift is wobbly", "status": "OPEN"},
            {"id": 3, "title": "Slow queries on user list", "description": "Spikes in transaction latency", "status": "RESOLVED"} # Resolved should be ignored
        ]
        
        # 1. High similarity match (Active ticket)
        is_dup, ticket_id, score = is_duplicate_ticket(
            issue_title="Office chair hydraulic lift is broken",
            issue_desc="The desk chair at desk 42 keeps sinking down.",
            existing_tickets=mock_tickets
        )
        self.assertTrue(is_dup)
        self.assertEqual(ticket_id, 2)
        self.assertGreaterEqual(score, 0.25)
        
        # 2. Ignored status match (Ticket #3 is RESOLVED, shouldn't flag duplicate)
        is_dup, ticket_id, score = is_duplicate_ticket(
            issue_title="Slow query performance warning",
            issue_desc="Latency is high on user endpoints",
            existing_tickets=mock_tickets
        )
        self.assertFalse(is_dup)
        
        # 3. Low similarity (No matches)
        is_dup, ticket_id, score = is_duplicate_ticket(
            issue_title="Docker daemon won't build container",
            issue_desc="Getting permissions errors on build execution",
            existing_tickets=mock_tickets
        )
        self.assertFalse(is_dup)

    def test_executor_direct_call(self):
        """Verify that the Executor can call MCP tools directly."""
        executor = Executor(mode="direct")
        
        # Test KB search
        kb_result_str = executor.execute_tool("search_kb", {"query": "VPN"})
        kb_articles = json.loads(kb_result_str)
        self.assertIsInstance(kb_articles, list)
        if len(kb_articles) > 0:
            self.assertIn("vpn.company.com", kb_articles[0]["answer"])
            
        # Test list tickets
        tickets_str = executor.execute_tool("list_tickets", {})
        tickets = json.loads(tickets_str)
        self.assertIsInstance(tickets, list)
        self.assertGreater(len(tickets), 0)

    def test_workflow_new_ticket_creation(self):
        """Verify that a unique issue runs the full ReAct loop and creates a ticket."""
        workflow = HelpdeskAgentWorkflow(mode="direct")
        issue_text = "Docker engine fails to launch container with permission error on start"
        
        # Execute workflow
        result = workflow.run(issue_text)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.state["created_ticket_id"])
        self.assertIsNone(result.state["added_comment_id"])
        
        # Verify in DB
        ticket_id = result.state["created_ticket_id"]
        db_ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        self.assertIsNotNone(db_ticket)
        self.assertEqual(db_ticket.title[:20], "Docker engine fails t"[:20])
        self.assertEqual(db_ticket.priority, "MEDIUM") # Classified due to 'error'
        self.assertEqual(db_ticket.status, "OPEN")
        
        # Clean up created ticket
        self.db.delete(db_ticket)
        self.db.commit()

    def test_workflow_duplicate_ticket_mitigation(self):
        """Verify that a duplicate issue triggers add_comment instead of a new ticket."""
        # Setup: Ensure an active ticket exists to match against
        test_ticket = Ticket(
            title="IntelliJ Idea license request keys",
            description="I need a license key for IntelliJ Idea ultimate package.",
            priority="LOW",
            status="OPEN",
            created_by=2 # mcp_user or normal user
        )
        self.db.add(test_ticket)
        self.db.commit()
        self.db.refresh(test_ticket)
        
        try:
            workflow = HelpdeskAgentWorkflow(mode="direct")
            duplicate_issue = "Requesting IntelliJ Idea license key for development work"
            
            result = workflow.run(duplicate_issue)
            self.assertTrue(result.success)
            self.assertEqual(result.state["duplicate_ticket_id"], test_ticket.id)
            self.assertTrue(result.state["is_duplicate"])
            self.assertIsNotNone(result.state["added_comment_id"])
            
            # Verify comment added to original ticket
            db_comment = self.db.query(Comment).filter(Comment.id == result.state["added_comment_id"]).first()
            self.assertIsNotNone(db_comment)
            self.assertEqual(db_comment.ticket_id, test_ticket.id)
            self.assertIn("Automated Agent Log: Same issue reported again.", db_comment.comment)
            
        finally:
            # Clean up
            self.db.delete(test_ticket)
            self.db.commit()

if __name__ == "__main__":
    unittest.main()
