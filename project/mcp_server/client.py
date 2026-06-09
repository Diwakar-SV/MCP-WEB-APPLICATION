import os
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_client_demo():
    print("=== STARTING TICKET SYSTEM MCP CLIENT DEMO ===")
    
    # Resolve the absolute path of the server script relative to this client
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "server.py")
    
    print(f"Connecting to MCP server at: {server_script}")
    
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env={**os.environ}
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            print("[Connected] Session initialized successfully.\n")
            
            # --- 1. LIST TOOLS ---
            print("--- 1. Listing Available Tools ---")
            tools_response = await session.list_tools()
            print(f"Server exposed {len(tools_response.tools)} tools:")
            for tool in tools_response.tools:
                print(f" - {tool.name}: {tool.description}")
            print()
            
            # --- 2. CREATE TICKET ---
            print("--- 2. Creating a Ticket via MCP ---")
            create_result = await session.call_tool(
                "create_ticket",
                arguments={
                    "title": "Cannot configure Git SSH Keys",
                    "description": "I followed the guides but keep getting Permission Denied (publickey) errors when pushing to github.com.",
                    "priority": "MEDIUM"
                }
            )
            
            create_response_text = create_result.content[0].text
            print("Create Ticket Tool Response:")
            print(create_response_text)
            print()
            
            # Extract ticket ID if creation was successful
            ticket_id = None
            try:
                data = json.loads(create_response_text)
                if "ticket" in data:
                    ticket_id = data["ticket"]["id"]
            except Exception as e:
                print("Could not parse ticket ID from response:", e)
                
            if not ticket_id:
                ticket_id = 1  # Fallback
                print(f"Fallback: using ticket_id = {ticket_id}")
                
            # --- 3. LIST TICKETS ---
            print("--- 3. Listing All Tickets ---")
            list_result = await session.call_tool("list_tickets")
            print("List Tickets Tool Response:")
            print(list_result.content[0].text)
            print()
            
            # --- 4. GET TICKET DETAIL ---
            print(f"--- 4. Getting Details for Ticket ID: {ticket_id} ---")
            get_result = await session.call_tool(
                "get_ticket",
                arguments={"ticket_id": ticket_id}
            )
            print("Get Ticket Tool Response:")
            print(get_result.content[0].text)
            print()
            
            # --- 5. ADD COMMENT ---
            print(f"--- 5. Adding Comment to Ticket ID: {ticket_id} ---")
            comment_result = await session.call_tool(
                "add_comment",
                arguments={
                    "ticket_id": ticket_id,
                    "comment": "Make sure your public key is added to GitHub settings and you are sshing as 'git@github.com', not your username."
                }
            )
            print("Add Comment Tool Response:")
            print(comment_result.content[0].text)
            print()
            
            # --- 6. SEARCH KNOWLEDGE BASE ---
            search_query = "VPN"
            print(f"--- 6. Searching Knowledge Base for: '{search_query}' ---")
            search_result = await session.call_tool(
                "search_kb",
                arguments={"query": search_query}
            )
            print("Search KB Tool Response:")
            print(search_result.content[0].text)
            print()
            
            # --- 7. UPDATE TICKET ---
            print(f"--- 7. Updating Ticket ID: {ticket_id} ---")
            update_result = await session.call_tool(
                "update_ticket",
                arguments={
                    "ticket_id": ticket_id,
                    "title": "Cannot configure Git SSH Keys (Resolved)",
                    "status": "RESOLVED"
                }
            )
            print("Update Ticket Tool Response:")
            print(update_result.content[0].text)
            print()

            # --- 8. DELETE TICKET (FAIL CASE: NOT CLOSED/RESOLVED) ---
            print("--- 8. Attempting to Delete Open Ticket #2 (Should Fail Verification) ---")
            delete_fail_result = await session.call_tool(
                "delete_ticket",
                arguments={"ticket_id": 2}
            )
            print("Delete Ticket Tool Response (Expected Failure):")
            print(delete_fail_result.content[0].text)
            print()

            # --- 9. DELETE TICKET (SUCCESS CASE: RESOLVED) ---
            print(f"--- 9. Deleting Resolved Ticket ID: {ticket_id} (Should Succeed) ---")
            delete_success_result = await session.call_tool(
                "delete_ticket",
                arguments={"ticket_id": ticket_id}
            )
            print("Delete Ticket Tool Response (Expected Success):")
            print(delete_success_result.content[0].text)
            print()

    print("=== MCP CLIENT DEMO COMPLETE ===")

if __name__ == "__main__":
    # Execute the client loop
    asyncio.run(run_mcp_client_demo())
