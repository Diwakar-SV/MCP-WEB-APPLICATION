import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional

# Add project root to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

class Executor:
    """
    Executes MCP tools.
    Supports two modes of execution:
    1. 'direct': Dynamic import and execution of local python functions (fast, reliable, database-backed).
    2. 'mcp': Spawn server.py as a subprocess and make standard Model Context Protocol JSON-RPC tool calls.
    """
    
    def __init__(self, mode: str = "direct"):
        self.mode = mode.lower()
        if self.mode not in ["direct", "mcp"]:
            self.mode = "direct"

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Synchronously executes the tool. Run asynchronously if in 'mcp' mode."""
        if self.mode == "direct":
            return self._execute_direct(tool_name, arguments)
        else:
            # Fallback to direct synchronous execution or wrap the async runner
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # If loop is already running (e.g. inside FastAPI), we must run in a thread or await it
                import threading
                from queue import Queue
                q = Queue()
                def worker():
                    val = asyncio.run(self._execute_mcp(tool_name, arguments))
                    q.put(val)
                t = threading.Thread(target=worker)
                t.start()
                t.join()
                return q.get()
            else:
                return loop.run_until_complete(self._execute_mcp(tool_name, arguments))

    def _execute_direct(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Imports and invokes the tool directly from the mcp_server/server.py module."""
        try:
            # Dynamically import mcp_server.server
            import mcp_server.server as server_module
            
            # Find the registered function
            # FastMCP tools are registered on the 'mcp' object
            # Let's see if we can find the function decorated or just call the python function directly
            tool_func = getattr(server_module, tool_name, None)
            if not tool_func:
                return json.dumps({"error": f"Tool '{tool_name}' not found on server module."})
            
            # Call the function with keyword arguments
            result = tool_func(**arguments)
            return result
        except Exception as e:
            return json.dumps({"error": f"Direct execution of tool '{tool_name}' failed: {str(e)}"})

    async def _execute_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Spawns the MCP server.py in a subprocess and invokes the tool via stdio ClientSession."""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            
            server_script = os.path.join(BASE_DIR, "mcp_server", "server.py")
            server_params = StdioServerParameters(
                command=sys.executable,  # Using current python executable
                args=[server_script],
                env={**os.environ}
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    # Call the tool using client session
                    result = await session.call_tool(tool_name, arguments=arguments)
                    
                    # Return the text response content
                    if result and result.content:
                        return result.content[0].text
                    return json.dumps({"error": "Empty response received from MCP server."})
        except Exception as e:
            # Fall back to direct execution if client protocol fails (e.g. package issues or Windows subprocess locks)
            print(f"[Executor Warning] MCP protocol client failed: {e}. Falling back to direct execution...")
            return self._execute_direct(tool_name, arguments)
