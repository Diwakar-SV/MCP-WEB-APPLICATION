# Helpdesk Ticket Management MCP System with AI Agent & Gemini Classification

A complete, production-grade Help Desk Ticket Management System powered by a React + TypeScript frontend, a Python FastAPI backend, a stateful ReAct (Reasoning + Acting) AI Agent, and an MCP (Model Context Protocol) server with Google Gemini-powered issue classification.

---

## 1. Executive Summary

### The Problem
Traditional helpdesk ticketing systems suffer from high operational latency, duplicate tickets, inconsistent priority labeling, and manual ticket routing. Support representatives spend a significant portion of their time triaging issues, checking for duplicate reports, searching internal knowledge bases, and copying instructions for users.

### The Solution
This project solves these challenges by combining a **Model Context Protocol (MCP)** server with an autonomous **AI Agent Layer** and **Google Gemini API Classification**. The system intercepts user support requests at entry and automates the entire triage lifecycle:
1. Automatically classifies the issue's priority, category, and summary using **Gemini-2.5-Flash**.
2. Conducts a Knowledge Base search for relevant resolution guidelines.
3. Automatically scans existing active tickets using Jaccard text similarity to identify duplicates.
4. Executes the ReAct (Reasoning + Acting) loop to dynamically choose whether to create a new ticket or append a comment to an existing duplicate, returning the final resolution directly to the user.

---

## 2. Features

* **Model Context Protocol (MCP) Integration:** Stdio-based FastMCP tool registration allowing Claude Desktop (or any MCP client) to inspect, create, update, and delete tickets and comments directly.
* **Autonomous AI Agent Workflow:** Stateful ReAct loop that coordinates thoughts and actions to solve issues.
* **Gemini-Powered Classification:** Uses Gemini-2.5-Flash with structured JSON schemas to extract priority (LOW, MEDIUM, HIGH, CRITICAL), incident category, and a concise summary.
* **Text Similarity Duplicate Detection:** Lightweight, local word-level Jaccard tokenization and title similarity analysis (60/40 weighted) to prevent database ticket duplication.
* **SQLite Persistence:** Clean relational schema with foreign key integrity constraints enforced via database triggers.
* **Multi-Tool Reasoning Engine:** Dual-mode executor supporting direct Python function execution inside FastAPI and RPC stdio subprocess connections.
* **Secure Telemetry Dashboard:** Responsive React dashboard visualizing status counts, daily ticket volume charts, and ticket details.

---

## 3. Architecture Overview

### Component Diagram

```
User (Web Portal) ──> React Client (SPA) ──> FastAPI Backend ──> Agent Workflow
                                                                      │
                                        ┌─────────────────────────────┴─────────────────────────────┐
                                        ▼                                                           ▼
                             Gemini API Classification                                  Executor (MCP Tool Bridge)
                           (Priority, Category, Summary)                                            │
                                                                       ┌────────────────────────────┴────────────────────────────┐
                                                                       ▼                                                         ▼
                                                               Direct function calls                                    Stdio MCP Protocol
                                                                       │                                                         │
                                                                       └────────────────────────────┬────────────────────────────┘
                                                                                                    ▼
                                                                                            FastMCP Server (Stdio)
                                                                                                    │
                                                                                                    ▼
                                                                                         SQLite Database (tickets.db)
```

### Component Responsibilities
1. **Frontend App (React + TypeScript + Vite):** A modern portal providing role-based routing (Admin vs User), ticket management UI, and analytics charts.
2. **Backend API (FastAPI):** Exposes JWT-secured REST controllers, endpoints for user auth, dashboard stats, and the `/api/agent/run` agentic invocation endpoint.
3. **AI Agent Layer (`agent/`):** Coordinates lifecycle stages. It feeds issue text into the Gemini classifier, updates `AgentState`, and drives the ReAct loop.
4. **FastMCP Server (`mcp_server/server.py`):** Registers and exposes ticket-system tools (`list_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `delete_ticket`, `add_comment`, `search_kb`).
5. **Database (`database/`):** Implements SQLite storage with SQLAlchemy models and an automated database seeding utility.

---

## 4. Project Structure

```text
project/
├── agent/
│   ├── __init__.py
│   ├── executor.py                 # Connects agent to MCP tools (direct or stdio)
│   ├── models.py                   # Pydantic schemas for AgentState and WorkflowResult
│   ├── planner.py                  # Priority classification rules & Jaccard duplicate detection
│   ├── prompts.py                  # System instructions for LLM ReAct loop
│   ├── test_agent.py               # Deterministic unit test suite
│   └── test_gemini_classifier.py   # Test suite mocking Gemini API and fallback logic
│
├── backend/
│   ├── auth.py                     # JWT token generation & bcrypt password hashing
│   ├── main.py                     # FastAPI server entry point and REST APIs
│   └── schemas.py                  # Pydantic validation schemas for API requests/responses
│
├── database/
│   ├── db.py                       # SQLite engine connection and session session generator
│   ├── models.py                   # SQLAlchemy database schemas
│   ├── seed.py                     # Table initialization and seed data generator
│   └── tickets.db                  # SQLite database file
│
├── docs/
│   ├── AGENT_ARCHITECTURE.md       # Detailed guide on the ReAct orchestrator loop
│   └── GEMINI_INTEGRATION.md       # Gemini sequence flows and interview preparation guide
│
├── frontend/                       # React TypeScript Vite single page app
│
├── mcp_server/
│   ├── server.py                   # FastMCP stdio tool server implementation
│   ├── client.py                   # Stdio client validation test script
│   └── claude_desktop_config.json  # Claude Desktop configuration setup guide
│
├── services/
│   └── gemini_classifier.py        # Gemini API connector and JSON classification parser
│
├── sample_data/                    # Sample inputs and expected classification outputs
│
├── .env                            # Local environment variables containing API keys (Ignored by Git)
├── .env.example                    # Template file for environment variable setup
├── .gitignore                      # Git exclusion rules for .env, PyCache, and DB temp files
├── AI_USAGE_NOTE.md                # Summary of AI usage, challenges, and prompts used
└── requirements.txt                # Python project dependencies
```

---

## 5. Technology Stack

| Technology | Purpose | Selection Rationale |
| :--- | :--- | :--- |
| **Python 3.10+** | Core runtime engine | Native support for advanced LLM libraries, web frameworks, and database connectors. |
| **Model Context Protocol (MCP)** | Decouples tools from LLM | Standardizes tool definitions using JSON-RPC, enabling any client (like Claude Desktop) to invoke them. |
| **SQLite / SQLAlchemy** | Database persistence | Zero-configuration database suited for quick setup, with SQLAlchemy protecting against SQL Injection. |
| **Gemini-2.5-Flash API** | Content generation & triage | High-speed, cost-effective API providing native structured JSON outputs (`response_mime_type`). |
| **Claude Desktop** | Developer UI / Integration | Real-world client that integrates with the FastMCP stdio server to act as a system administrator. |
| **python-dotenv** | Configuration management | Securely loads keys from `.env` on disk to prevent hardcoded API secrets. |
| **FastAPI / Uvicorn** | Backend service delivery | Asynchronous web framework that parses request payloads and serves REST endpoints quickly. |
| **React / TypeScript / Vite** | Web User Interface | Provides a strong, typed component system and high performance rendering. |

---

## 6. Setup Instructions

### Prerequisites
* **Python 3.10+** (globally accessible via terminal)
* **Node.js v18+** & npm v9+
* **Claude Desktop** (Optional, to test MCP stdio connectivity)
* **Google Gemini API Key** (Obtained from Google AI Studio)

### Installation
From the repository root:
1. **Install Python dependencies:**
   ```bash
   pip install -r project/requirements.txt
   ```
2. **Initialize and Seed the Database:**
   ```bash
   python project/database/seed.py
   ```
3. **Configure Environment Variables:**
   Create a `.env` file in the `project/` directory:
   ```bash
   GEMINI_API_KEY="your_api_key_here"
   ```
4. **Install Node modules for the Frontend:**
   ```bash
   cd project/frontend
   npm install
   cd ../..
   ```

---

## 7. Run Instructions

### 1. Launch FastAPI Backend Server
From the repository root:
```bash
uvicorn project.backend.main:app --reload --port 8000
```
* Backend starts at `http://localhost:8000`.
* Telemetry REST endpoints will reload automatically upon code changes.

### 2. Launch React Frontend App
Open a new terminal window, navigate to the `frontend` folder, and start the Vite dev server:
```bash
cd project/frontend
npm run dev
```
* Open your browser and navigate to the address output in the terminal (typically `http://localhost:5173`).
* Use these login credentials:
  * **Admin:** `admin@example.com` / Password: `admin123`
  * **Normal User:** `user@example.com` / Password: `user123`

### 3. Connect to Claude Desktop
Add the configuration from `project/mcp_server/claude_desktop_config.json` to your Claude Desktop config file:
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ticket-system": {
      "command": "python",
      "args": [
        "c:/Users/diwak/OneDrive/Desktop/MCP WEB APPLICATION/project/mcp_server/server.py"
      ]
    }
  }
}
```
*Replace the path above with the absolute path to your `server.py` file.* Restart Claude Desktop.

---

## 8. Usage Guide

### Scenario 1: Ticket Triage Flow
1. Submit an issue: `"Our production billing service is throwing HTTP 500 errors."`
2. The agent runs the Gemini classifier and labels the priority as `CRITICAL`, category as `Billing`, and sets the summary to `"Production billing service HTTP 500 outage"`.
3. The system checks database tickets, identifies that this is a new issue, and creates a ticket with the summary and `CRITICAL` priority.

### Scenario 2: Duplicate Ticket Mitigation
1. A user reports: `"FastAPI is slow and throwing query timeouts."`
2. The agent queries tickets, and finds an existing active ticket with the title: `"Slow query warnings and transaction timeouts"`.
3. The Jaccard Jaccard coefficient computes an overlap score of `40%` (above the `25%` threshold).
4. The agent adds a comment to the existing ticket rather than opening a new duplicate.

---

## 9. AI Agent Workflow Lifecycle

```
[User Request] ──> [Gemini Classifier] ──> [Query KB (search_kb)] ──> [List Tickets (list_tickets)] 
                                                                              │
                                                                              ▼
                                                                  [Run Jaccard Check]
                                                                              │
                                       ┌──────────────────────────────────────┴──────────────────────────────────────┐
                                       ▼                                                                             ▼
                             [Similarity >= 25%]                                                            [Similarity < 25%]
                                       │                                                                             │
                                       ▼                                                                             ▼
                        [Comment on Duplicate Ticket]                                                  [Create New Support Ticket]
                                       │                                                                             │
                                       └──────────────────────────────────────┬──────────────────────────────────────┘
                                                                              ▼
                                                                 [Generate Final Response]
```

---

## 10. Gemini Classification Details

### Prompt Design
The prompt provides context rules that direct Gemini-2.5-Flash to return only valid JSON mapping the target keys:
```text
You are an expert Helpdesk Support Assistant.
Analyze the following user support issue:
"{issue_text}"
Determine:
1. Urgency and business impact to assign priority: LOW, MEDIUM, HIGH, or CRITICAL.
2. The incident category (e.g. "Software", "Hardware", "Network", "Access/Security", "Billing", "General").
3. A short, professional summary.
Return format:
{
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "category": "string",
  "summary": "string"
}
```

### Graceful Fallback Strategy
If Gemini encounters network outages or API limits (e.g. HTTP 429), the workflow catches the error:
* **Priority:** Reverts to the rule-based keyword classifier in `planner.py`.
* **Category:** Falls back to `"General"`.
* **Summary:** Truncates the issue text to 80 characters.
The ticket lifecycle proceeds normally without stopping.

---

## 11. Database Schema Design

### Database Relationships

```
┌─────────────────┐             ┌─────────────────┐
│     users       │             │    tickets      │
├─────────────────┤             ├─────────────────┤
│ id (PK)         │1 ──────────*│ id (PK)         │
│ username        │             │ title           │
│ email           │             │ description     │
│ password        │             │ status          │
│ role            │             │ priority        │
└─────────────────┘             │ created_at      │
                                │ updated_at      │
                                │ created_by (FK) │
                                └────────┬────────┘
                                         │1
                                         │
                                         │*
                                ┌────────▼────────┐
                                │    comments     │
                                ├─────────────────┤
                                │ id (PK)         │
                                │ ticket_id (FK)  │
                                │ comment         │
                                │ author          │
                                │ created_at      │
                                └─────────────────┘
```

---

## 12. Security Considerations

* **Secrets Management:** The `GEMINI_API_KEY` is loaded from a local `.env` file that is excluded from version control via `.gitignore`.
* **Input Validation:** API payloads are validated using Pydantic schemas, preventing SQL Injection and malformed formats.
* **Scope Resolution:** Regular users can only query and modify their own tickets. Administrative privileges are enforced for operations like ticket deletion.

---

## 13. Interview Discussion Guide

### Q: Why use the ReAct (Reason + Act) pattern for a support agent?
> **Answer:** The ReAct pattern blends reasoning thoughts with actionable tool calls. Instead of executing backend database changes blindly, the agent describes *why* it chooses a tool, executes it, and analyzes the observations before deciding on the next step. This mimics human troubleshooting, preventing ticket duplication and locating FAQ answers.

### Q: Why decouple the classifier service from the database models?
> **Answer:** This keeps the system cohesive and prevents breaking API contracts. The database `Ticket` model does not need to store in-memory fields like `category` or `summary`. Instead, these are maintained in the memory-only `AgentState` schema and mapped during the tool-execution phase. This keeps the schema clean and avoids database migration overhead.

---

## 14. Troubleshooting

* **Vite Dev Server connection issues:** If the frontend shows connection errors, ensure the FastAPI server is running on port `8000` and has CORS enabled.
* **Gemini API Error 403 / 400:** Make sure your `GEMINI_API_KEY` is set correctly in `project/.env` and has no trailing whitespaces.
* **Claude Desktop hammer icon missing:** Verify the absolute path to your python executable and the `server.py` path inside `claude_desktop_config.json`. Restart Claude Desktop.

---

## 15. License & Acknowledgements

* **License:** Licensed under the MIT Open Source License.
* **Acknowledgements:** Powered by FastMCP, FastAPI, SQLite, and Google Gemini API.
