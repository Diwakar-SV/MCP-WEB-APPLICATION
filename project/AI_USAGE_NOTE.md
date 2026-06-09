# AI Usage Note: Helpdesk Ticket Management MCP System

This document outlines the collaborative role of Artificial Intelligence (AI) and human engineering in building, debugging, and documenting the Helpdesk Ticket Management Model Context Protocol (MCP) System.

---

## 1. AI Tools Used

During the lifecycle of this project, several AI assistants and APIs were utilized:
*   **Antigravity:** Used as the primary agentic coding assistant for code generation, workspace navigation, multi-file refactoring, implementation planning, and system verification.
*   **Claude Desktop:** Acted as the runtime environment for hosting and testing the FastMCP server, allowing the agent to test stdio-based tool execution directly within an interactive environment.
*   **ChatGPT:** Assisted with initial architectural patterns, boilerplate structure scaffolding, and interactive schema design.
*   **Gemini API (Gemini-2.5-Flash):** Integrated programmatically into the backend workflow to perform automated ticket classification, priority labeling, and summary extraction.

---

## 2. What AI Helped With

AI models accelerated development by providing high-quality code generation and design ideas:
*   **MCP Server Structure:** Assisted in setting up the Model Context Protocol (MCP) server structure using `FastMCP`, registering SQLite database tools (`list_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `add_comment`), and a knowledge base search tool (`search_kb`).
*   **Agent Workflow Design:** Guided the design of the stateful ReAct (Reasoning + Acting) loop, ensuring proper state progression, validation logic, and transition conditions inside the agent layer.
*   **Documentation Generation:** Automatically drafted comprehensive guides like [AGENT_ARCHITECTURE.md](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/docs/AGENT_ARCHITECTURE.md) and [GEMINI_INTEGRATION.md](file:///c:/Users/diwak/OneDrive/Desktop/MCP%20WEB%20APPLICATION/project/docs/GEMINI_INTEGRATION.md), detailing sequence flows and system setup.
*   **Boilerplate Code:** Generated initial FastAPI controller files, Pydantic data schemas, SQLAlchemy SQLite models, and starter frontend components.

---

## 3. What AI Got Wrong

While AI dramatically speeded up implementation, human-in-the-loop verification and manual debugging were essential:
*   **Incorrect File Paths:** AI frequently generated absolute paths pointing to default placeholders or different workspaces (e.g., in `claude_desktop_config.json` and imports) instead of dynamically resolving the local project path.
*   **Missing Imports:** Generated code blocks occasionally omitted necessary library imports (such as `typing` helpers or `FastAPI` exceptions) or introduced circular dependencies between model schemas and API routes.
*   **Required Manual Debugging:** Database transaction scripts had errors where unique constraint violations occurred during parallel runs, needing manual database trigger adjustments and `try-except` blocks.
*   **Needed Human Verification:** Complex configurations—like CORS origins, JWT expiration times, secret key loading, and the Jaccard similarity threshold value—required human oversight to verify they met security and business requirements.

---

## 4. Best Prompts Used

These prompts were highly effective in achieving correct and structured outputs from the LLMs:

### A. MCP Architecture Prompt
> "Write a stdio-based MCP server using the FastMCP Python SDK that exposes a SQLite database for helpdesk ticket management. The server should register tools to read, write, update, and search tickets and comments. Provide a JSON configuration file template that can be loaded into Claude Desktop to interact with the server locally."

### B. Agent Workflow Prompt
> "Design a stateful ReAct (Reasoning + Acting) loop for a support agent in Python. The agent must first classify a ticket, query a knowledge base for answers, search the active database for duplicate tickets using a similarity threshold, and then decide whether to comment on a duplicate or create a new ticket, explaining its thoughts at each step."

### C. Gemini Integration Prompt
> "Create a Python service `gemini_classifier.py` that interfaces with the Google Gemini API (specifically `gemini-2.5-flash`). Force the output to be a structured JSON object containing keys for `priority`, `category`, and `summary` by configuring `response_mime_type='application/json'`. Implement a fallback to local keyword classification rules and default values if the API key is missing or the request fails."
