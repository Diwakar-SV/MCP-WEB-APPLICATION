import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClassifier:
    """
    Connects to the Google Gemini API to classify incoming helpdesk issues
    into structured priority, category, and summary fields.
    """
    def __init__(self):
        # API key will be read from environment variable
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("GEMINI_API_KEY environment variable is not set. GeminiClassifier will not function.")

    def classify_issue(self, issue_text: str) -> dict:
        """
        Send the issue text to Gemini API and parse structured JSON response.
        Expected output format:
        {
            "priority": "LOW|MEDIUM|HIGH|CRITICAL",
            "category": "string",
            "summary": "string"
        }
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Constructing the system prompt and instructions
        prompt = f"""
You are an expert Helpdesk Support Assistant. 
Analyze the following user support issue:
"{issue_text}"

Evaluate:
1. Urgency and business impact to assign a priority: LOW, MEDIUM, HIGH, or CRITICAL.
   - Outages, security breaches, and production system down issues are CRITICAL.
   - Core feature failures, severe performance issues, or security warnings are HIGH.
   - Application errors, slow responses, or non-blocking bugs are MEDIUM.
   - How-to questions, setup questions, request for documentation, or minor requests are LOW.
2. The incident category (e.g. "Software", "Hardware", "Network", "Access/Security", "Billing", "General").
3. A short, professional summary.

You MUST return a valid JSON object with the following exact keys and format:
{{
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "category": "string",
  "summary": "string"
}}
"""
        try:
            # Using the fast, low-latency gemini-2.5-flash model
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Requesting json output format
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            text_response = response.text.strip()
            logger.info(f"Gemini raw classification response: {text_response}")
            
            # Parse and validate the response
            result = json.loads(text_response)
            
            # Ensure keys exist
            priority = result.get("priority", "LOW").upper()
            if priority not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                priority = "LOW"
                
            category = result.get("category", "General")
            summary = result.get("summary", issue_text[:80])
            
            return {
                "priority": priority,
                "category": category,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Failed to classify issue with Gemini API: {str(e)}")
            raise e

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    # services/gemini_classifier.py is in project/services/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    
    test_issue = "Production database is down and throws ORA-00600 error"
    if len(sys.argv) > 1:
        test_issue = " ".join(sys.argv[1:])
        
    print(f"Testing GeminiClassifier with: '{test_issue}'")
    classifier = GeminiClassifier()
    try:
        res = classifier.classify_issue(test_issue)
        print("Success! Classification result:")
        print(json.dumps(res, indent=2))
    except Exception as err:
        print(f"Error: {err}")
