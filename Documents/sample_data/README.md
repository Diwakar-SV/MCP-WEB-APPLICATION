# Helpdesk Sample Data

This directory contains representative test cases for validating the AI Agent's classification, categorization, and duplicate mitigation workflow.

## Directory Structure

```text
sample_data/
├── README.md               # This documentation file
├── input_issue_1.txt       # Raw text of a new, critical payment issue
├── expected_output_1.json  # Expected classification & creation action
├── input_issue_2.txt       # Raw text of a slow database query warning
└── expected_output_2.json  # Expected high-priority classification & comment action
```

---

## Test Cases

### Case 1: Critical Payment System Outage (New Ticket)
*   **Input File:** [input_issue_1.txt](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/sample_data/input_issue_1.txt)
*   **Description:** A severe issue indicating business-critical systems are down.
*   **Expected Results ([expected_output_1.json](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/sample_data/expected_output_1.json)):**
    ```json
    {
      "priority": "CRITICAL",
      "category": "Payments",
      "action": "Create Ticket"
    }
    ```

### Case 2: Query Timeout Warning (Duplicate Verification)
*   **Input File:** [input_issue_2.txt](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/sample_data/input_issue_2.txt)
*   **Description:** An issue description similar to existing active tickets in the seeded database (overlapping words trigger similarity detection).
*   **Expected Results ([expected_output_2.json](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/sample_data/expected_output_2.json)):**
    ```json
    {
      "priority": "HIGH",
      "category": "Software",
      "action": "Comment on Ticket"
    }
    ```

---

## Usage in Testing

These sample files can be fed into custom test scripts or agent evaluation runs to ensure the LLM parser and database triggers function identically under test constraints:

```bash
# Example verification script execution
python project/agent/test_agent.py
```
