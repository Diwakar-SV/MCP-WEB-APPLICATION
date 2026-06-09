import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.gemini_classifier import GeminiClassifier
from agent.workflow import HelpdeskAgentWorkflow
from database.db import SessionLocal
from database.models import Ticket

class TestGeminiClassifier(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    @patch.dict(os.environ, {}, clear=True)
    def test_classifier_raises_value_error_without_api_key(self):
        """Verify that the classifier raises ValueError when API key is missing."""
        classifier = GeminiClassifier()
        # Ensure it raises ValueError because api_key is None
        with self.assertRaises(ValueError):
            classifier.classify_issue("Test issue")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "mock-api-key"})
    @patch("google.generativeai.GenerativeModel")
    def test_classifier_returns_structured_json(self, mock_model_class):
        """Verify that the classifier parses and returns structured JSON output from Gemini API."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"priority": "CRITICAL", "category": "Billing", "summary": "Payment system outage"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        classifier = GeminiClassifier()
        result = classifier.classify_issue("Production payment system is down")

        self.assertEqual(result["priority"], "CRITICAL")
        self.assertEqual(result["category"], "Billing")
        self.assertEqual(result["summary"], "Payment system outage")

        # Verify default key validation behavior if model returns invalid priority
        mock_response.text = '{"priority": "SUPER-URGENT", "category": "Billing", "summary": "Payment outage"}'
        result_invalid_priority = classifier.classify_issue("Production payment system is down")
        self.assertEqual(result_invalid_priority["priority"], "LOW") # Defaults to LOW if priority is invalid

    @patch.dict(os.environ, {"GEMINI_API_KEY": "mock-api-key"})
    @patch("google.generativeai.GenerativeModel")
    def test_workflow_integrates_gemini_classification(self, mock_model_class):
        """Verify that workflow uses classification output for ticket creation."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"priority": "HIGH", "category": "Access/Security", "summary": "Duo MFA failed"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        workflow = HelpdeskAgentWorkflow(mode="direct")
        workflow.gemini_key = None # Force deterministic loop for classification testing
        issue_text = "I cannot login using Duo security app code"
        result = workflow.run(issue_text)

        self.assertTrue(result.success)
        self.assertEqual(result.state["priority"], "HIGH")
        self.assertEqual(result.state["category"], "Access/Security")
        self.assertEqual(result.state["summary"], "Duo MFA failed")
        self.assertIsNotNone(result.state["created_ticket_id"])

        # Verify DB ticket title matches summary
        ticket_id = result.state["created_ticket_id"]
        db_ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        self.assertIsNotNone(db_ticket)
        self.assertEqual(db_ticket.title, "Duo MFA failed")
        self.assertEqual(db_ticket.priority, "HIGH")

        # Cleanup
        self.db.delete(db_ticket)
        self.db.commit()

    @patch.dict(os.environ, {"GEMINI_API_KEY": "mock-api-key"})
    @patch("google.generativeai.GenerativeModel")
    def test_workflow_fallback_on_gemini_failure(self, mock_model_class):
        """Verify that workflow falls back to rule-based classification if Gemini API raises exception."""
        # Force generate_content to raise an Exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Quota Exceeded")
        mock_model_class.return_value = mock_model

        workflow = HelpdeskAgentWorkflow(mode="direct")
        workflow.gemini_key = None # Force deterministic loop for fallback testing
        issue_text = "Database outage in production environment"
        
        # This should execute rule-based classification and complete ticket creation
        result = workflow.run(issue_text)

        self.assertTrue(result.success)
        # Verify fallback values: rule-based priority for "outage" is "CRITICAL"
        self.assertEqual(result.state["priority"], "CRITICAL")
        self.assertEqual(result.state["category"], "General")
        self.assertEqual(result.state["summary"][:20], "Database outage in p"[:20])
        self.assertIsNotNone(result.state["created_ticket_id"])

        # Verify DB
        ticket_id = result.state["created_ticket_id"]
        db_ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        self.assertIsNotNone(db_ticket)
        self.assertEqual(db_ticket.title[:20], "Database outage in p"[:20])
        self.assertEqual(db_ticket.priority, "CRITICAL")

        # Cleanup
        self.db.delete(db_ticket)
        self.db.commit()

if __name__ == "__main__":
    unittest.main()
