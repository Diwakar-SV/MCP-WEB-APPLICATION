import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from agent.models import AgentState, ExecutionStep, WorkflowResult
from agent.planner import classify_priority, generate_plan, is_duplicate_ticket
from agent.executor import Executor
import agent.prompts as prompts
from services.gemini_classifier import GeminiClassifier

# Load environment variables from .env if present (relative to project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class HelpdeskAgentWorkflow:
    """
    Orchestrates the ReAct (Reason + Act) loop for resolving user support tickets.
    """
    
    def __init__(self, mode: str = "direct"):
        self.executor = Executor(mode=mode)
        # Check for Gemini API key to enable live LLM reasoning
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        # Initialize the Gemini Classifier
        self.classifier = GeminiClassifier()


    def run(self, issue_text: str) -> WorkflowResult:
        """Runs the complete ReAct loop for a given issue text."""
        # Initialize State
        state = AgentState(
            issue_text=issue_text,
            status="RUNNING"
        )
        # Determine priority, category, and summary with Gemini or fall back
        try:
            if self.classifier.api_key:
                print(f"[Agent] Classifying issue using Gemini: '{issue_text}'")
                classification = self.classifier.classify_issue(issue_text)
                state.priority = classification["priority"]
                state.category = classification["category"]
                state.summary = classification["summary"]
            else:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")
        except Exception as e:
            print(f"[Agent Error] Gemini classification failed: {e}. Falling back to rule-based classification.")
            state.priority = classify_priority(issue_text)
            state.category = "General"
            state.summary = issue_text[:80] + ("..." if len(issue_text) > 80 else "")
        
        try:
            if self.gemini_key:
                print(f"[Agent] Starting Live LLM Reasoning Loop for issue: '{issue_text}'")
                self._run_live_llm_loop(state)
            else:
                print(f"[Agent] Starting Local Deterministic Reasoning Loop for issue: '{issue_text}'")
                self._run_simulated_loop(state)
                
            state.status = "COMPLETED"
            return WorkflowResult(
                success=True,
                final_response=state.final_response or "Ticket processed successfully.",
                steps=state.history,
                state=state.model_dump()
            )
        except Exception as e:
            print(f"[Agent Error] Workflow execution failed: {e}")
            state.status = "FAILED"
            # Return a graceful degradation result
            fallback_response = f"I'm sorry, I encountered an error while processing your issue. However, I have registered it in our system under the priority '{state.priority}'."
            return WorkflowResult(
                success=False,
                final_response=fallback_response,
                steps=state.history,
                state=state.model_dump()
            )

    def _run_simulated_loop(self, state: AgentState):
        """Runs the deterministic rule-based ReAct simulator."""
        issue = state.issue_text
        priority = state.priority
        
        # --- STEP 1: THINK & SEARCH KB ---
        step1_thought = f"I need to check the Knowledge Base using search_kb() to see if there is any troubleshooting advice or standard procedure for '{issue}'."
        step1_action = "search_kb(query)"
        
        # Perform query extraction
        # Simple extraction: take first 2-3 words or words representing issue
        words = [w for w in issue.split() if len(w) > 2][:3]
        query = " ".join(words) if words else issue
        
        # Execute tool
        kb_response_str = self.executor.execute_tool("search_kb", {"query": query})
        
        # Parse KB
        kb_articles = []
        try:
            kb_articles = json.loads(kb_response_str)
        except:
            pass
        state.kb_results = kb_articles
        
        state.history.append(ExecutionStep(
            step_number=1,
            thought=step1_thought,
            action=f"search_kb(query='{query}')",
            observation=kb_response_str
        ))
        
        # --- STEP 2: THINK & LIST TICKETS ---
        step2_thought = "I have examined the Knowledge Base. Now, before creating a new ticket, I should check the list of active support tickets in the system using list_tickets() to verify if a similar issue was already reported by another user."
        
        # Execute tool
        tickets_response_str = self.executor.execute_tool("list_tickets", {})
        
        existing_tickets = []
        try:
            existing_tickets = json.loads(tickets_response_str)
        except:
            pass
        state.matching_tickets = existing_tickets
        
        state.history.append(ExecutionStep(
            step_number=2,
            thought=step2_thought,
            action="list_tickets()",
            observation=f"Retrieved {len(existing_tickets)} active tickets from database."
        ))
        
        # --- STEP 3: THINK, DECIDE & EXECUTE (CREATE vs COMMENT) ---
        # Perform similarity algorithm
        is_dup, duplicate_id, similarity_score = is_duplicate_ticket(issue, issue, existing_tickets)
        state.is_duplicate = is_dup
        state.duplicate_ticket_id = duplicate_id
        
        if is_dup and duplicate_id:
            # Duplicate ticket found! Add Comment.
            step3_thought = f"My text similarity algorithm matches this issue to Ticket #{duplicate_id} with {int(similarity_score * 100)}% confidence. To prevent ticket duplication, I should add a comment to the existing ticket."
            comment_text = f"Automated Agent Log: Same issue reported again. Issue details: '{issue}'. Classification: {priority} Priority."
            
            tool_args = {"ticket_id": duplicate_id, "comment": comment_text}
            comment_response_str = self.executor.execute_tool("add_comment", tool_args)
            
            try:
                comment_data = json.loads(comment_response_str)
                if "comment" in comment_data:
                    state.added_comment_id = comment_data["comment"]["id"]
            except:
                pass
                
            state.history.append(ExecutionStep(
                step_number=3,
                thought=step3_thought,
                action=f"add_comment(ticket_id={duplicate_id}, comment='{comment_text}')",
                observation=comment_response_str
            ))
            
            # --- STEP 4: FINAL RESPONSE ---
            kb_guide = ""
            if kb_articles:
                kb_guide = f"\n\n**Troubleshooting Instructions:**\n{kb_articles[0].get('answer')}"
                
            state.final_response = (
                f"Thank you for reporting this. I detected a similar open ticket in our database (Ticket #{duplicate_id}). "
                f"To keep all updates unified, I have added a comment to that ticket instead of creating a duplicate one. "
                f"Our IT operations team is actively addressing it.{kb_guide}"
            )
            
        else:
            # New issue! Create ticket.
            step3_thought = f"No similar active tickets were found (highest similarity score: {int(similarity_score * 100)}%). I will create a new support ticket in the system with '{priority}' priority."
            
            title = state.summary if state.summary else (issue[:80] + ("..." if len(issue) > 80 else ""))
            tool_args = {
                "title": title,
                "description": issue,
                "priority": priority
            }
            create_response_str = self.executor.execute_tool("create_ticket", tool_args)
            
            try:
                ticket_data = json.loads(create_response_str)
                if "ticket" in ticket_data:
                    state.created_ticket_id = ticket_data["ticket"]["id"]
            except:
                pass
                
            state.history.append(ExecutionStep(
                step_number=3,
                thought=step3_thought,
                action=f"create_ticket(title='{tool_args['title']}', description='...', priority='{priority}')",
                observation=create_response_str
            ))
            
            # --- STEP 4: FINAL RESPONSE ---
            kb_guide = ""
            if kb_articles:
                kb_guide = f"\n\n**Troubleshooting Guidance:**\n{kb_articles[0].get('answer')}"
            else:
                kb_guide = "\n\nWe will review your request and get back to you shortly."
                
            state.final_response = (
                f"A new support ticket has been created for your issue: **Ticket #{state.created_ticket_id}** "
                f"with a priority level of **{priority}**. Our team has been notified.{kb_guide}"
            )

    def _run_live_llm_loop(self, state: AgentState):
        """Runs the live ReAct loop powered by the Gemini API."""
        issue = state.issue_text
        priority = state.priority
        
        # Standard system prompt + instructions
        messages = [
            {"role": "system", "content": prompts.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"User Issue: '{issue}'\n"
                           f"Detected Priority: {priority}\n"
                           f"Detected Category: {state.category}\n"
                           f"Generated Summary: {state.summary}"
            }
        ]
        
        # Max 5 reasoning steps to avoid infinite loops
        for step_idx in range(1, 6):
            # Format history for LLM
            history_str = ""
            for prev_step in state.history:
                history_str += f"\nThought: {prev_step.thought}\nAction: {prev_step.action}\nObservation: {prev_step.observation}\n"
                
            prompt = f"""
            Current ReAct Loop step. Below is the execution history so far:
            {history_str}
            
            Generate the next step. You MUST output a valid JSON object with the following schema:
            {{
                "thought": "your thought string here detailing what you need to do and why",
                "action": "search_kb | list_tickets | create_ticket | add_comment | respond",
                "arguments": {{
                     "query": "search term (required for search_kb)",
                     "ticket_id": integer_id (required for add_comment),
                     "comment": "comment text (required for add_comment)",
                     "title": "ticket title (required for create_ticket)",
                     "description": "ticket description (required for create_ticket)",
                     "priority": "LOW/MEDIUM/HIGH/CRITICAL (required for create_ticket)"
                }},
                "final_response": "polite final response text summarizing everything (required ONLY if action is 'respond')"
            }}
            
            Make sure to return ONLY the raw JSON text. No markdown blocks.
            """
            
            llm_text = self._call_gemini_api(prompt, messages)
            try:
                # Clean markdown codeblocks from JSON if LLM returned them
                cleaned_json = llm_text.replace("```json", "").replace("```", "").strip()
                action_data = json.loads(cleaned_json)
            except Exception as e:
                print(f"[Agent Warning] Failed to parse LLM JSON: '{llm_text}'. Error: {e}. Falling back to simulation...")
                self._run_simulated_loop(state)
                return
                
            thought = action_data.get("thought", "")
            action = action_data.get("action", "respond")
            arguments = action_data.get("arguments", {})
            
            if action == "respond":
                state.final_response = action_data.get("final_response", "Issue processed.")
                # Log final step
                state.history.append(ExecutionStep(
                    step_number=step_idx,
                    thought=thought,
                    action="respond()",
                    observation="Responding to user with summary."
                ))
                break
                
            # Execute tool
            observation_str = ""
            if action == "search_kb":
                query = arguments.get("query", issue)
                observation_str = self.executor.execute_tool("search_kb", {"query": query})
                try:
                    state.kb_results = json.loads(observation_str)
                except: pass
            elif action == "list_tickets":
                observation_str = self.executor.execute_tool("list_tickets", {})
                try:
                    state.matching_tickets = json.loads(observation_str)
                except: pass
            elif action == "add_comment":
                ticket_id = arguments.get("ticket_id")
                comment = arguments.get("comment", "")
                observation_str = self.executor.execute_tool("add_comment", {"ticket_id": ticket_id, "comment": comment})
                try:
                    comment_data = json.loads(observation_str)
                    if "comment" in comment_data:
                        state.added_comment_id = comment_data["comment"]["id"]
                        state.duplicate_ticket_id = ticket_id
                        state.is_duplicate = True
                except: pass
            elif action == "create_ticket":
                title = arguments.get("title", issue[:80])
                desc = arguments.get("description", issue)
                pri = arguments.get("priority", priority)
                observation_str = self.executor.execute_tool("create_ticket", {"title": title, "description": desc, "priority": pri})
                try:
                    t_data = json.loads(observation_str)
                    if "ticket" in t_data:
                        state.created_ticket_id = t_data["ticket"]["id"]
                except: pass
            else:
                observation_str = f"Unknown action: {action}"
                
            # Log execution step
            state.history.append(ExecutionStep(
                step_number=step_idx,
                thought=thought,
                action=f"{action}({json.dumps(arguments)})",
                observation=observation_str
            ))

    def _call_gemini_api(self, prompt: str, history: List[Dict[str, str]]) -> str:
        """Call Gemini API using urllib (standard library) to prevent package dependency bloat."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        # Construct content structure for Gemini API
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        # Add the current prompt instructions as a user request
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                # Parse gemini output
                candidates = res_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                raise Exception("Invalid API response format")
        except urllib.error.HTTPError as e:
            print(f"[Gemini API HTTP Error] Status: {e.code}, Response: {e.read().decode('utf-8')}")
            raise
        except Exception as e:
            print(f"[Gemini API Connection Error] {e}")
            raise
