import asyncio
from typing import Optional, Dict, Any, List, Union, Callable, Awaitable
from contextlib import AsyncExitStack
import os
import base64
import random

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
from loguru import logger
import json

load_dotenv()  # load environment variables from .env

# Check if ANTHROPIC_API_KEY is loaded
if not os.getenv("ANTHROPIC_API_KEY"):
    logger.warning("ANTHROPIC_API_KEY not found in environment variables. Please check your .env file.")



# Icon mapping cache
_icon_mapping_cache = None
_icons_base64_cache = {}

def load_icon_mapping():
    """Load tool icon mapping from JSON file"""
    global _icon_mapping_cache
    if _icon_mapping_cache is None:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_path = os.path.join(current_dir, "user_client", "icons", "tool_metadata.json")
            with open(mapping_path, 'r', encoding='utf-8') as f:
                _icon_mapping_cache = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load icon mapping: {e}")
            _icon_mapping_cache = {"mappings": {}, "default": ""}
    return _icon_mapping_cache

def get_tool_icon_base64(tool_name: str, server_name: str = None) -> Optional[str]:
    """Get icon for a tool based on server name or tool name, encoded as base64 data URI"""
    global _icons_base64_cache
    
    try:
        # Load mapping
        mapping = load_icon_mapping()
        mappings = mapping.get("mappings", {})
        default_config = mapping.get("default", {})
        
        # Get tool configuration - try server name first, then tool name
        tool_config = None
        if server_name:
            tool_config = mappings.get(server_name)
        if not tool_config:
            tool_config = mappings.get(tool_name)
        if not tool_config and default_config:
            tool_config = default_config
        
        if not tool_config:
            return None
        
        # Extract icon path (handle both old string format and new object format)
        if isinstance(tool_config, str):
            icon_path = tool_config
        elif isinstance(tool_config, dict):
            icon_path = tool_config.get("icon")
        else:
            return None
            
        if not icon_path:
            return None
            
        # Check cache first
        if icon_path in _icons_base64_cache:
            return _icons_base64_cache[icon_path]
        
        # Load SVG file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_icon_path = os.path.join(current_dir, "user_client", "icons", icon_path)
        
        if os.path.exists(full_icon_path):
            with open(full_icon_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                # Encode SVG content to base64
                svg_bytes = svg_content.encode('utf-8')
                base64_svg = base64.b64encode(svg_bytes).decode('utf-8')
                data_uri = f"data:image/svg+xml;base64,{base64_svg}"
                _icons_base64_cache[icon_path] = data_uri
                return data_uri
        else:
            logger.warning(f"Icon file not found: {full_icon_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error loading icon for tool {tool_name}: {e}")
        return None

def get_tool_comment(tool_name: str, server_name: str = None) -> Optional[str]:
    """Get comment for a tool based on server name or tool name.
    Always returns a non-empty default message if specific mapping is unavailable.
    """
    try:
        # Load mapping
        mapping = load_icon_mapping()
        mappings = mapping.get("mappings", {})
        default_config = mapping.get("default", {})

        # Get tool configuration - try server name first, then tool name
        tool_config = None
        if server_name:
            tool_config = mappings.get(server_name)
        if not tool_config:
            tool_config = mappings.get(tool_name)

        # Extract comment when available
        comment: Optional[str] = None
        if isinstance(tool_config, dict):
            comment = tool_config.get("comment")

        # Fallback to default mapping comment
        if not comment and isinstance(default_config, dict):
            comment = default_config.get("comment")

        # Final hard-coded fallback
        if not comment or not str(comment).strip():
            comment = "정보를 검색하고 있습니다."

        return comment
    except Exception as e:
        logger.error(f"Error loading comment for tool {tool_name}: {e}")
        return "정보를 검색하고 있습니다."

class BaseMCPClientError(Exception):
    """Base exception for MCP Client errors"""
    pass

class BaseMCPServerConnection:
    """Base MCP server connection"""
    def __init__(self, server_id: str, config: Union[str, Dict[str, Any]]):
        self.server_id = server_id
        self.config = config
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.is_connected = False
        self.stdio = None
        self.write = None
        
    async def connect(self):
        """Connect to this specific server"""
        try:
            command: str
            args: List[str]
            server_display_name: str
            env: Optional[Dict[str, str]] = None

            if isinstance(self.config, str):
                # Handle local script path
                server_script_path = self.config
                is_python = server_script_path.endswith('.py')
                is_js = server_script_path.endswith('.js')
                if not (is_python or is_js):
                    raise BaseMCPClientError("Server script must be a .py or .js file")

                command = "python" if is_python else "node"
                args = [server_script_path]
                server_display_name = f"{self.server_id}: {server_script_path}"
            
            elif isinstance(self.config, dict):
                # Handle external server config from JSON
                command = self.config.get("command")
                args = self.config.get("args", [])
                env = self.config.get("env")
                
                server_display_name = f"{self.server_id}: {command} {' '.join(args)}"
                if not command:
                    raise BaseMCPClientError("Server configuration must include a 'command'")

                # If it's a docker command, append the image name
                if command == "docker":
                    image = self.config.get("image")
                    if not image:
                        raise BaseMCPClientError("Docker server config must include an 'image' name")
                    args.append(image)
                    server_display_name += f" {image}"

            else:
                raise BaseMCPClientError(f"Unsupported server configuration type: {type(self.config)}")

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )

            logger.info(f"Connecting to MCP server: {server_display_name}")
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await self.session.initialize()
            self.is_connected = True

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            tool_names = [tool.name for tool in tools]
            logger.info(f"Connected to {server_display_name} with {len(tool_names)} tools: {tool_names}")
            
        except Exception as e:
            self.is_connected = False
            logger.error(f"Failed to connect to MCP server {self.server_id}: {str(e)}")
            raise BaseMCPClientError(f"Connection failed for {self.server_id}: {str(e)}") from e
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools from this server"""
        if not self.is_connected or not self.session:
            return []
        
        try:
            response = await self.session.list_tools()
            return [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
        except Exception as e:
            logger.error(f"Error getting tools from {self.server_id}: {str(e)}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a tool on this server"""
        if not self.is_connected or not self.session:
            raise BaseMCPClientError(f"Server {self.server_id} not connected")
        
        return await self.session.call_tool(tool_name, arguments)
    
    async def cleanup(self):
        """Clean up this connection"""
        if not self.is_connected:
            return
            
        logger.debug(f"Starting cleanup for server {self.server_id}")
        
        try:
            self.is_connected = False
            
            if self.session:
                self.session = None
            
            self.stdio = None
            self.write = None
            
            if self.exit_stack:
                try:
                    await asyncio.wait_for(self.exit_stack.aclose(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout during exit_stack cleanup for {self.server_id}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in [
                        "different task", 
                        "cancel scope", 
                        "cancelled", 
                        "task was destroyed",
                        "event loop is closed"
                    ]):
                        logger.debug(f"Ignoring expected cleanup error for {self.server_id}: {e}")
                    else:
                        logger.error(f"Unexpected cleanup error for {self.server_id}: {e}")
                        raise
                finally:
                    try:
                        self.exit_stack = AsyncExitStack()
                    except Exception:
                        self.exit_stack = None
                        
            logger.debug(f"Cleanup completed for server {self.server_id}")
                    
        except Exception as e:
            logger.error(f"Critical error during cleanup of {self.server_id}: {str(e)}")
            self.is_connected = False

class BaseMCPClient:
    """Base MCP Client with common functionality"""
    def __init__(self, system_prompt_filename: str, model: str = "claude-sonnet-4-20250514"):
        self.server_connections: Dict[str, BaseMCPServerConnection] = {}
        self.anthropic = Anthropic()
        self.tool_to_server_map: Dict[str, str] = {}
        self.system_prompt_filename = system_prompt_filename
        self.system_prompt = self.load_system_prompt()
        self.model = model
        logger.info(f"{self.__class__.__name__} initialized (model={self.model})")
    
    
    def load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to find the prompt file in the calling module's directory
            parent_dir = os.path.dirname(current_dir)
            
            # Try multiple potential locations
            potential_paths = [
                os.path.join(parent_dir, "mcp_clients", "user_client", self.system_prompt_filename),
                os.path.join(parent_dir, "mcp_clients", "genui_client", self.system_prompt_filename),
                os.path.join(current_dir, self.system_prompt_filename),
            ]
            
            for prompt_file_path in potential_paths:
                if os.path.exists(prompt_file_path):
                    with open(prompt_file_path, 'r', encoding='utf-8') as f:
                        _system_prompt = f.read().strip()
                        logger.debug(f"System prompt loaded from {prompt_file_path}")
                        return _system_prompt
            
            # If no file found, return a default prompt
            logger.warning(f"System prompt file '{self.system_prompt_filename}' not found in any location")
            return "You are a helpful AI assistant."
            
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return "You are a helpful AI assistant."
    
    async def add_server(self, server_id: str, server_config: Union[str, Dict[str, Any]]):
        """Add and connect to a new server"""
        if server_id in self.server_connections:
            logger.warning(f"Server {server_id} already exists, replacing...")
            await self.remove_server(server_id)
        
        connection = BaseMCPServerConnection(server_id, server_config)
        try:
            await connection.connect()
            self.server_connections[server_id] = connection
            
            tools = await connection.get_tools()
            logger.info(f"Server {server_id} provides {len(tools)} tools")
            
            logger.info(f"Successfully added server {server_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add server {server_id}: {str(e)}")
            return False
    
    async def remove_server(self, server_id: str):
        """Remove a server connection"""
        if server_id not in self.server_connections:
            logger.warning(f"Server {server_id} not found for removal")
            return
            
        logger.info(f"Removing server {server_id}")
        connection = self.server_connections[server_id]
        
        tools_to_remove = [tool_name for tool_name, sid in self.tool_to_server_map.items() if sid == server_id]
        for tool_name in tools_to_remove:
            del self.tool_to_server_map[tool_name]
        
        del self.server_connections[server_id]
        
        try:
            await asyncio.wait_for(connection.cleanup(), timeout=10.0)
            logger.info(f"Successfully removed server {server_id}")
        except asyncio.TimeoutError:
            logger.warning(f"Timeout during removal of server {server_id}")
        except Exception as e:
            logger.error(f"Error during cleanup of removed server {server_id}: {str(e)}")

    async def ensure_connected(self):
        """Ensure at least one server is connected"""
        connected_servers = [sid for sid, conn in self.server_connections.items() if conn.is_connected]
        if not connected_servers:
            raise BaseMCPClientError("No servers are connected")
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from all connected servers"""
        try:
            await self.ensure_connected()
            all_tools = []
            
            for server_id, connection in self.server_connections.items():
                if connection.is_connected:
                    tools = await connection.get_tools()
                    for tool in tools:
                        tool_name = tool["name"]
                        self.tool_to_server_map[tool_name] = server_id
                        all_tools.append(tool)
            
            logger.debug(f"Returning {len(all_tools)} tools from all servers")
            return all_tools
        except Exception as e:
            logger.error(f"Error getting available tools: {str(e)}")
            raise BaseMCPClientError(f"Failed to get tools: {str(e)}") from e
    
    @property
    def is_connected(self) -> bool:
        """Check if any server is connected"""
        return any(conn.is_connected for conn in self.server_connections.values())
    
    async def _execute_single_tool_call(self, tool_call):
        """Execute a single tool call with configurable return format"""
        start_time = asyncio.get_event_loop().time()
        tool_name, tool_args, tool_id = tool_call.name, tool_call.input, tool_call.id
        
        try:
 
            server_id = self.tool_to_server_map.get(tool_name)
            if not server_id or server_id not in self.server_connections:
                raise BaseMCPClientError(f"No server found for tool '{tool_name}'")
            
            server_connection = self.server_connections[server_id]
            if not server_connection.is_connected:
                raise BaseMCPClientError(f"Server '{server_id}' is not connected")
            
            result = await server_connection.call_tool(tool_name, tool_args)
            
            # Extract text content from CallToolResult
            tool_result = ""
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                if hasattr(first_content, 'text'):
                    tool_result = first_content.text
                else:
                    tool_result = str(first_content)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000  # Convert to milliseconds
            
            logger.info(f"[TOOL] Tool Execution: {tool_name}")
            logger.info(f"  └─ Args: {tool_args}")
            logger.info(f"  └─ ID: {tool_id}")
            logger.info(f"  └─ Result: {tool_result[:300]}{'...' if len(tool_result) > 300 else ''}")
            logger.info(f"  └─ Execution time: {execution_time:.1f}ms")
            
            server_name = server_id.replace("external_", "").replace("custom_", "")
            
            result_data = {
                "tool_name": f'{server_name}.{tool_name}',
                "tool_args": tool_args,
                "tool_result": tool_result
            }
            
            return result_data, None
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"Error executing tool {tool_name}: {e}")
            
            error_content = f"Error executing tool: {e}"
            
            server_name = server_id.replace("external_", "").replace("custom_", "")
            
            error_result = {
                "tool_name": f'{server_name}.{tool_name}',
                "tool_args": tool_args,
                "tool_result": error_content,
                "error": str(e)
            }
            
            return error_result, e
    
    async def cleanup(self):
        """Clean up all server connections"""
        logger.info(f"Cleaning up {self.__class__.__name__} resources...")
        
        if not self.server_connections:
            logger.info("No server connections to clean up")
            return
        
        self.tool_to_server_map.clear()
        server_ids = list(self.server_connections.keys())
        
        for server_id in server_ids:
            connection = self.server_connections.get(server_id)
            if connection:
                try:
                    await asyncio.wait_for(connection.cleanup(), timeout=3.0)
                    logger.info(f"Successfully cleaned up server {server_id}")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout cleaning up server {server_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up server {server_id}: {str(e)}")
                finally:
                    try:
                        if server_id in self.server_connections:
                            del self.server_connections[server_id]
                    except Exception:
                        pass
        
        self.server_connections.clear()
        self.tool_to_server_map.clear()
        
        logger.info(f"{self.__class__.__name__} cleanup completed")
    
    async def _run_initial_sequential_thinking(
        self,
        query: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        tool_results: List[Dict[str, Any]],
        on_update: Optional[Callable[[str], Awaitable[None]]] = None,
        multi_agent_expression: dict[str, List[str]] = {}
    ) -> None:
        """Run sequentialthinking tool once before any other tool calls.
        Adds a textual summary of the result to messages to preserve API semantics.
        """
        try:
            sequential_tool = next((tool for tool in available_tools if tool.get('name') == 'sequentialthinking'), None)
            if not sequential_tool:
                logger.warning("Sequential thinking tool not available")
                return

            logger.info("[FORCE] Starting with mandatory sequentialthinking tool call")
            import uuid

            class MockToolCall:
                def __init__(self, name, input_data, id):
                    self.name = name
                    self.input = input_data
                    self.id = id

            sequential_call = MockToolCall(
                'sequentialthinking',
                {
                    'thought': f"I need to analyze the user's request: {' '.join([f'{k}: {v}' for k, v in query.items()])}. Let me think about what information I need to gather and which tools to use.",
                    'nextThoughtNeeded': False,
                    'thoughtNumber': 1,
                    'totalThoughts': 1,
                    'isRevision': False
                },
                f"sequential_thinking_{uuid.uuid4().hex[:8]}"
            )
            
            # Execute tool call without on_update to avoid duplicate messages
            result, error = await self._execute_single_tool_call(sequential_call)
            tool_results.append(result)

            # Sequential thinking을 첫 번째 assistant 응답과 tool 결과로 처리
            # Mock assistant response for sequential thinking
            mock_assistant_content = [
                {
                    "type": "tool_use",
                    "id": sequential_call.id,
                    "name": "sequentialthinking",
                    "input": sequential_call.input
                }
            ]
            messages.append({"role": "assistant", "content": mock_assistant_content})
            
            # Sequential thinking 결과를 tool_result로 처리
            tool_result_text = result.get("tool_result", "") if isinstance(result, dict) else str(result)
            tool_result_content = [{
                "type": "tool_result",
                "tool_use_id": sequential_call.id,
                "content": tool_result_text
            }]
            messages.append({"role": "user", "content": tool_result_content})


        except Exception as e:
            logger.error(f"Failed to execute mandatory sequentialthinking: {e}")

    async def process_query_list(
        self,
        query: dict,
        model: str,
        on_update: Optional[Callable[[str], Awaitable[None]]] = None,
        multi_agent_expression: dict[str, List[str]] = {}
    ) -> List[Dict[str, Any]]:
        """
        Query Claude with available tools and return a list of tool execution results.
        This replaces the legacy streaming behavior with a simple list return.
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": '\n'.join([f"{k}: {v}" for k, v in query.items()])
                }
            ]

            available_tools = await self.get_available_tools()
            logger.debug(f"Using {len(available_tools)} tools for list processing.")

            max_iterations = 40
            tool_results: List[Dict[str, Any]] = []

            # 무조건 sequentialthinking을 먼저 실행 (별도 함수)
            await self._run_initial_sequential_thinking(query, available_tools, messages, tool_results, on_update, multi_agent_expression)
            on_update_gpt_worker_tasks = []
            
            for _ in range(max_iterations):
                response = self.anthropic.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=self.system_prompt,
                    messages=messages,
                    tools=available_tools,
                    temperature=0.1
                )

                tool_calls = [content for content in response.content if content.type == 'tool_use']

                if not tool_calls:
                    break

                messages.append({"role": "assistant", "content": response.content})

                tasks = [asyncio.create_task(self._execute_single_tool_call(tool_call)) for tool_call in tool_calls]
                
                # Start separate on_update worker that calls GPT before sending updates
                if on_update:
                    async def _on_update_gpt_worker(tool_calls):
                        from core.llm import call_llm
                        import json
                        import re

                        expressions_list = multi_agent_expression.get('p3') or []

                        def _to_plain_text(text) -> str:
                            if text is None:
                                return ""
                            result = str(text).strip()
                            # Extract from fenced code block if entire string is fenced
                            fenced = re.fullmatch(r"```(?:\w+)?\n([\s\S]*?)\n```", result)
                            if fenced:
                                result = fenced.group(1).strip()
                            # Strip surrounding single/double quotes if the whole string is quoted
                            if (result.startswith('"') and result.endswith('"')) or (result.startswith("'") and result.endswith("'")):
                                result = result[1:-1].strip()
                            # Collapse whitespace/newlines to single spaces
                            result = re.sub(r"\s+", " ", result).strip()
                            return result

                        def _fallback_fill_slots(template_text: str) -> str:
                            # 간단한 규칙으로 [slot] 치환 (안전한 일반화 단어 사용)
                            text = str(template_text or "").strip()
                            if not text:
                                return text
                            def _replace_slot(match):
                                slot_raw = match.group(0)
                                slot = slot_raw.strip("[]").lower()
                                if "date" in slot or "timeframe" in slot or "day" in slot:
                                    return "today"
                                if "location" in slot or "place" in slot or "region" in slot:
                                    return "nearby"
                                if any(k in slot for k in ["keyword", "subject", "query", "tag"]):
                                    return "keyword"
                                if any(k in slot for k in ["name", "contact", "friend", "artist", "profile"]):
                                    return "contact"
                                if "device" in slot:
                                    return "device"
                                if any(k in slot for k in ["playlist", "video", "folder", "file"]):
                                    return slot
                                if "category" in slot:
                                    return "category"
                                if any(k in slot for k in ["order", "item"]):
                                    return slot
                                return "recent"
                            return re.sub(r"\[[^\]]+\]", _replace_slot, text)

                        try:
                            for single_call in tool_calls:
                                # Build safe context dict for GPT processing
                                safe_ctx = {
                                    "name": getattr(single_call, 'name', ''),
                                    "input": getattr(single_call, 'input', {}),
                                }
                                
                                # Rename tool for better user experience
                                if safe_ctx["name"] == 'brave_web_search' or 'brave' in safe_ctx["name"].lower():
                                    safe_ctx["name"] = 'internet search'
                                    
                                candidates = [{"index": i, "text": t} for i, t in enumerate(expressions_list)]
                                prompt = (
                                    "Role: Choose ONE best-fitting progress message from candidates for the current MCP tool execution.\n"
                                    "You MUST pick from the candidates and replace any [slot]s.\n\n"
                                    "Slot replacement rules:\n"
                                    "- Slots may look like [keyword], [date range], [location], [name], [subject], [device], [playlist], [video], [query], [place], [category], [order], [item].\n"
                                    "- Replace slots with concise, generic phrases inferred from the tool name and input.\n"
                                    "- NEVER copy raw parameter values, IDs, URLs, filenames.\n"
                                    "- Prefer generalized words like 'today', 'recent', 'nearby', 'keyword', 'contact'.\n\n"
                                    "Style guidelines:\n"
                                    "- Exactly one sentence, present progressive, ≤ 7 words.\n"
                                    "- No counts, limits, IDs, or bracket text.\n"
                                    "- Output plain text only. No quotes or markdown.\n\n"
                                    f"Context:\nTool call: { json.dumps(safe_ctx, ensure_ascii=False, default=str) }\n"
                                    f"Query: { json.dumps(query, ensure_ascii=False, default=str) }\n\n"
                                    f"Candidates (JSON array):\n{ json.dumps(candidates, ensure_ascii=False) }\n\n"
                                    "Output: The chosen line with slots replaced, plain text only."
                                )

                                gpt_text = await call_llm(prompt, model_name="gpt-4.1-mini")
                                clean_text = _to_plain_text(gpt_text)
                                logger.info(clean_text)
                                if clean_text:
                                    await on_update(clean_text)
                                else:
                                    try:
                                        seed = json.dumps({"tool": safe_ctx.get("name"), "input": safe_ctx.get("input")}, ensure_ascii=False, default=str)
                                        import hashlib
                                        idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest()[:8], 16)
                                        sel = expressions_list[idx % max(1, len(expressions_list))] if expressions_list else "I'm checking now."
                                        await on_update(_fallback_fill_slots(sel))
                                    except Exception:
                                        await on_update("I'm checking now.")
                        except Exception as e:
                            logger.error(f"Error in _on_update_gpt_worker: {e}")
                            
                    on_update_gpt_worker_tasks.append(asyncio.create_task(_on_update_gpt_worker(tool_calls)))
                                    

                for completed_task in asyncio.as_completed(tasks):
                    try:
                        result, error = await completed_task
                        tool_results.append(result)
                        logger.info(f"[TOOL] Tool completed")
                    except Exception as e:
                        logger.error(f"Tool execution exception: {e}")


                tool_result_content = []
                for i, result in enumerate(tool_results[-len(tool_calls):]):  # Only get results from current iteration
                    if i < len(tool_calls):
                        tool_use_id = tool_calls[i].id
                        
                        tool_result_text = result.get("tool_result", "") if isinstance(result, dict) else str(result)
                        tool_result_content.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": tool_result_text
                        })

                if tool_result_content:
                    messages.append({"role": "user", "content": tool_result_content})
                else:
                    logger.warning("[TOOL] No tool results to add to messages")

            if on_update_gpt_worker_tasks:
                for task in on_update_gpt_worker_tasks:
                    await task

            return tool_results

        except Exception as e:
            import traceback
            logger.error(f"Error in process_query_list: {traceback.format_exc()}")
            logger.error(f"Error in process_query_list: {e}")
            raise BaseMCPClientError(f"List query processing failed: {e}") from e