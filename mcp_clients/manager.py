import json
import os
from typing import Optional, List, Dict, Any
from loguru import logger
from .client import BaseMCPClient, BaseMCPClientError

class BaseMCPManagerError(Exception):
    """Base exception for MCP Manager errors"""
    pass

class BaseMCPManager:
    """Base MCP Manager with common functionality"""
    
    def __init__(self, client_class=None, system_prompt_filename: str = None):
        self.custom_mcp_server_paths: List[str] = []
        self.external_mcp_servers: Dict[str, Any] = {}
        self.mcp_client_instance: Optional[BaseMCPClient] = None
        self.client_class = client_class or BaseMCPClient
        self.system_prompt_filename = system_prompt_filename
        logger.info(f"{self.__class__.__name__} initialized")
    
    def load_custom_mcp_servers(self, base_dir: str = None) -> List[str]:
        """Load all custom MCP server scripts under custom_mcp_servers directory (recursively)."""
        if base_dir is None:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'user_client', 'custom_mcp_servers')
            )

        if not os.path.exists(base_dir):
            logger.warning(f"Custom MCP servers directory not found: {base_dir}")
            return []

        collected_scripts: List[str] = []
        for current_dir, dirnames, filenames in os.walk(base_dir):
            # Skip typical cache directories
            dirnames[:] = [d for d in dirnames if d != '__pycache__']

            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                # Ignore package markers, hidden helper scripts, and utility modules
                if (filename == '__init__.py' or 
                    filename.startswith('_') or 
                    filename in ['common_utils.py', 'utils.py', 'helpers.py']):
                    continue
                collected_scripts.append(os.path.join(current_dir, filename))

        # Sort for deterministic order
        collected_scripts.sort()
        return collected_scripts
    
    def load_external_mcp_servers(self, json_path: str) -> Dict[str, Any]:
        """Load external MCP servers from JSON file (official format)"""
        if not os.path.exists(json_path):
            logger.warning(f"External MCP server config not found: {json_path}")
            return {}
        
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('mcpServers', {})
    
    async def connect_to_servers(self, custom_servers: bool = True, external_servers: bool = True):
        """Connect to custom and/or external servers"""
        total_expected = 0
        total_connected = 0
        failed_servers = []
        
        # Count expected servers
        if custom_servers:
            total_expected += len(self.custom_mcp_server_paths)
        if external_servers:
            total_expected += len([s for s in self.external_mcp_servers.values() if not s.get('disabled', False)])
        
        # Connect to custom servers
        if custom_servers and self.custom_mcp_server_paths:
            logger.info("Connecting to custom MCP servers...")
            for server_path in self.custom_mcp_server_paths:
                server_name = os.path.basename(server_path)
                if server_name.endswith('.py'):
                    server_name = server_name[:-3]  # .py 제거
                server_id = f"custom_{server_name}"
                
                logger.info(f"Connecting to custom server {server_id}: {server_name}")
                
                try:
                    success = await self.mcp_client_instance.add_server(server_id, server_path)
                    if success:
                        total_connected += 1
                        logger.info(f"Successfully connected to custom server: {server_name}")
                    else:
                        failed_servers.append(f"custom server '{server_name}'")
                        logger.error(f"Failed to connect to custom server: {server_name}")
                except Exception as e:
                    failed_servers.append(f"custom server '{server_name}' - {str(e)}")
                    logger.error(f"Error connecting to custom server {server_name}: {str(e)}")
        
        # Connect to external servers
        if external_servers and self.external_mcp_servers:
            logger.info("Connecting to external MCP servers...")
            for server_name, server_config in self.external_mcp_servers.items():
                if server_config.get('disabled', False):
                    logger.info(f"⏸️ Skipping disabled external server: {server_name}")
                    continue
                
                server_id = f"external_{server_name}"
                logger.info(f"Connecting to external server {server_id}: {server_name}")
                
                try:
                    success = await self.mcp_client_instance.add_server(server_id, server_config)
                    if success:
                        total_connected += 1
                        logger.info(f"✅ Successfully connected to external server: {server_name}")
                    else:
                        failed_servers.append(f"external server '{server_name}'")
                        logger.error(f"❌ Failed to connect to external server: {server_name}")
                except Exception as e:
                    failed_servers.append(f"external server '{server_name}' - {str(e)}")
                    logger.error(f"❌ Error connecting to external server {server_name}: {str(e)}")
        
        return total_connected, total_expected, failed_servers
    
    async def init_mcp_client(self, custom_servers: bool = True, external_servers: bool = True, 
                             custom_base_dir: str = None, external_config_path: str = None):
        """Initialize MCP client with specified server types"""
        try:
            # Load server configs
            if custom_servers:
                self.custom_mcp_server_paths = self.load_custom_mcp_servers(custom_base_dir)
                logger.info(f"Found {len(self.custom_mcp_server_paths)} custom MCP servers")
            
            if external_servers and external_config_path:
                self.external_mcp_servers = self.load_external_mcp_servers(external_config_path)
                logger.info(f"Found {len(self.external_mcp_servers)} external MCP servers")
            
            # Initialize MCP client
            if self.system_prompt_filename:
                self.mcp_client_instance = self.client_class(self.system_prompt_filename)
            else:
                raise BaseMCPManagerError("system_prompt_filename is required for MCP client initialization")
            
            # Connect to servers
            total_connected, total_expected, failed_servers = await self.connect_to_servers(
                custom_servers, external_servers
            )
            
            # Check if any server failed to connect
            if failed_servers:
                error_msg = f"Failed to connect to {len(failed_servers)} server(s): {', '.join(failed_servers)}"
                logger.error(error_msg)
                logger.error("Shutting down application due to server connection failures")
                raise BaseMCPManagerError(error_msg)
            
            if total_connected > 0:
                logger.info(f"MCP Client initialized successfully with {total_connected}/{total_expected} servers connected")
                
                # Log connected servers and available tools
                connected_servers = [sid for sid, conn in self.mcp_client_instance.server_connections.items() if conn.is_connected]
                logger.info(f"Connected servers: {connected_servers}")
                
                try:
                    available_tools = await self.mcp_client_instance.get_available_tools()
                    tool_summary = {}
                    for tool in available_tools:
                        tool_name = tool["name"]
                        server_id = self.mcp_client_instance.tool_to_server_map.get(tool_name, 'unknown')
                        server_id = server_id.replace("external_", "").replace("custom_", "")
                        if server_id not in tool_summary:
                            tool_summary[server_id] = []
                        tool_summary[server_id].append(tool_name)
                    
                    logger.info("Available tools by server:")
                    for server_id, tools in tool_summary.items():
                        logger.info(f"  {server_id}: {tools}")
                        
                except Exception as e:
                    logger.warning(f"Could not list available tools: {str(e)}")
                
                return True
            else:
                error_msg = "No MCP servers were successfully connected"
                logger.error(error_msg)
                logger.error("Shutting down application - no servers available")
                raise BaseMCPManagerError(error_msg)
                
        except BaseMCPManagerError:
            raise
        except Exception as e:
            error_msg = f"Failed to initialize MCP client: {e}"
            logger.error(error_msg)
            logger.error("Shutting down application due to initialization error")
            raise BaseMCPManagerError(error_msg) from e
    
    async def cleanup_mcp_client(self):
        """Cleanup MCP client resources"""
        if self.mcp_client_instance:
            try:
                await self.mcp_client_instance.cleanup()
                logger.info("MCP Client cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during MCP client cleanup: {e}")
            finally:
                self.mcp_client_instance = None
    
    @property
    def is_connected(self) -> bool:
        """Check if MCP client is connected"""
        return (self.mcp_client_instance and self.mcp_client_instance.is_connected)
    
    def _format_tools_for_guide(self, tools: List[Dict[str, Any]]) -> List[str]:
        """Helper to format tool information for the markdown guide"""
        content = []
        if tools:
            # 1. 도구 목록 테이블
            content.append("### Available Tools")
            content.append("")
            content.append("| Function Name | Description | Parameters |")
            content.append("|---------------|-------------|------------|")
            
            for tool in tools:
                name = tool.get('name', 'N/A')
                description = tool.get('description', 'No description')
                
                # 설명에서 줄바꿈을 <br>로 변환하고 들여쓰기 제거
                description = description.replace('\n', '<br>').replace('    ', '')
                
                # 파라미터 정보 추출 및 포맷팅
                params = []
                input_schema = tool.get('input_schema', {})
                properties = input_schema.get('properties', {})
                required = input_schema.get('required', [])
                
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', '').replace('\n', ' ').strip()
                    is_required = param_name in required
                    req_mark = "*" if is_required else ""
                    params.append(f"- **{param_name}{req_mark}** ({param_type}): {param_desc}")
                
                params_str = "<br>".join(params) if params else "None"
                
                content.append(f"| {name} | {description} | {params_str} |")
            
            content.append("")
            
            # 2. 상세 설명 섹션
            content.append("### Detailed Descriptions")
            content.append("")
            
            for tool in tools:
                name = tool.get('name', 'N/A')
                description = tool.get('description', 'No description')
                
                content.append(f"#### {name}")
                content.append("")
                content.append(description)
                content.append("")
                
                # 파라미터 상세 설명
                input_schema = tool.get('input_schema', {})
                properties = input_schema.get('properties', {})
                required = input_schema.get('required', [])
                
                if properties:
                    content.append("**Parameters:**")
                    content.append("")
                    for param_name, param_info in properties.items():
                        param_type = param_info.get('type', 'unknown')
                        param_desc = param_info.get('description', '')
                        is_required = param_name in required
                        req_mark = " (required)" if is_required else ""
                        
                        content.append(f"- **{param_name}**{req_mark}")
                        content.append(f"  - Type: `{param_type}`")
                        content.append(f"  - Description: {param_desc}")
                        content.append("")
                
                content.append("---")
                content.append("")
        else:
            content.append("No tools available")
            content.append("")
        
        return content

    async def generate_mcp_guide(self):
        """Generate MCP guide with available tools information"""
        from datetime import datetime
        
        guide_content = []
        guide_content.append("# MCP Servers Guide")
        guide_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        guide_content.append("")
        
        # Connection Status Summary
        guide_content.append("## Connection Status Summary")
        guide_content.append("")
        
        if self.mcp_client_instance and self.mcp_client_instance.server_connections:
            connected_count = sum(1 for conn in self.mcp_client_instance.server_connections.values() if conn.is_connected)
            total_count = len(self.mcp_client_instance.server_connections)
            guide_content.append(f"**Connected Servers**: {connected_count}/{total_count}")
            guide_content.append("")
            
            # 서버별 상태 표시
            guide_content.append("| Server ID | Status | Type |")
            guide_content.append("|-----------|--------|------|")
            
            for server_id, connection in self.mcp_client_instance.server_connections.items():
                status = "Connected" if connection.is_connected else "Not Connected"
                server_type = "Custom" if server_id.startswith("custom_") else "External"
                display_id = server_id.replace("external_", "").replace("custom_", "")
                guide_content.append(f"| {display_id} | {status} | {server_type} |")
            
            guide_content.append("")
        else:
            guide_content.append("**No servers initialized**")
            guide_content.append("")
        
        # Custom MCP Servers section
        guide_content.append("## Custom MCP Servers")
        guide_content.append("")
        
        if self.custom_mcp_server_paths:
            for server_path in self.custom_mcp_server_paths:
                server_name = os.path.basename(server_path)
                if server_name.endswith('.py'):
                    server_name = server_name[:-3]
                
                if 'mcp_servers' in server_path:
                    relative_path = server_path[server_path.find('mcp_servers'):]
                    relative_path = relative_path.replace('\\', '/')
                else:
                    relative_path = os.path.basename(server_path)
                
                guide_content.append(f"### {server_name}")
                guide_content.append(f"**Path**: `{relative_path}`")
                
                server_id = f"custom_{server_name}"
                if (self.mcp_client_instance and 
                    server_id in self.mcp_client_instance.server_connections and
                    self.mcp_client_instance.server_connections[server_id].is_connected):
                    guide_content.append("**Status**: Connected")
                else:
                    guide_content.append("**Status**: Not Connected")
                
                guide_content.append("")
                
                try:
                    tools = None
                    if (self.mcp_client_instance and 
                        server_id in self.mcp_client_instance.server_connections and
                        self.mcp_client_instance.server_connections[server_id].is_connected):
                        connection = self.mcp_client_instance.server_connections[server_id]
                        tools = await connection.get_tools()
                    else:
                        from .client import BaseMCPServerConnection
                        temp_connection = BaseMCPServerConnection(server_id, server_path)
                        await temp_connection.connect()
                        tools = await temp_connection.get_tools()
                        await temp_connection.cleanup()
                    
                    guide_content.extend(self._format_tools_for_guide(tools))
                    
                except Exception as e:
                    guide_content.append(f"Error connecting to server: {str(e)}")
                
                guide_content.append("")
        else:
            guide_content.append("No custom MCP servers found.")
            guide_content.append("")
        
        # External MCP Servers section
        guide_content.append("## External MCP Servers")
        guide_content.append("")
        
        if self.external_mcp_servers:
            for server_name, server_config in self.external_mcp_servers.items():
                server_id = f"external_{server_name}"
                guide_content.append(f"### {server_name}")
                guide_content.append(f"**Command**: `{server_config.get('command', 'N/A')}`")
                guide_content.append(f"**Args**: `{' '.join(server_config.get('args', []))}`")
                guide_content.append(f"**Disabled**: {server_config.get('disabled', False)}")
                
                if (self.mcp_client_instance and 
                    server_id in self.mcp_client_instance.server_connections and
                    self.mcp_client_instance.server_connections[server_id].is_connected):
                    guide_content.append("**Status**: Connected")
                elif server_config.get('disabled', False):
                    guide_content.append("**Status**: Disabled")
                else:
                    guide_content.append("**Status**: Not Connected")
                
                guide_content.append("")
                
                if not server_config.get('disabled', False):
                    try:
                        tools = None
                        if (self.mcp_client_instance and 
                            server_id in self.mcp_client_instance.server_connections and
                            self.mcp_client_instance.server_connections[server_id].is_connected):
                            connection = self.mcp_client_instance.server_connections[server_id]
                            tools = await connection.get_tools()
                        else:
                            from .client import BaseMCPServerConnection
                            temp_connection = BaseMCPServerConnection(server_id, server_config)
                            await temp_connection.connect()
                            tools = await temp_connection.get_tools()
                            await temp_connection.cleanup()
                        
                        guide_content.extend(self._format_tools_for_guide(tools))

                    except Exception as e:
                        guide_content.append(f"Error connecting to server: {str(e)}")
                        guide_content.append("")
                else:
                    guide_content.append("*Server is disabled*")
                    guide_content.append("")
        else:
            guide_content.append("No external MCP servers configured.")
            guide_content.append("")
        
        # All Available Tools Summary
        if self.mcp_client_instance and self.mcp_client_instance.is_connected:
            guide_content.append("## All Available Tools Summary")
            guide_content.append("")
            
            try:
                all_tools = await self.mcp_client_instance.get_available_tools()
                if all_tools:
                    tools_by_server = {}
                    for tool in all_tools:
                        tool_name = tool["name"]
                        server_id = self.mcp_client_instance.tool_to_server_map.get(tool_name, 'unknown')
                        server_id = server_id.replace("external_", "").replace("custom_", "")
                        if server_id not in tools_by_server:
                            tools_by_server[server_id] = []
                        tools_by_server[server_id].append(tool)
                    
                    for server_id, tools in tools_by_server.items():
                        guide_content.append(f"### {server_id}")
                        guide_content.append("")
                        guide_content.extend(self._format_tools_for_guide(tools))
                    
                    guide_content.append(f"**Total Available Tools**: {len(all_tools)}")
                else:
                    guide_content.append("No tools available from connected servers.")
            except Exception as e:
                guide_content.append(f"Error retrieving tools summary: {str(e)}")
        
        # Write to file
        try:
            with open('mcp_guide.md', 'w', encoding='utf-8') as f:
                f.write('\n'.join(guide_content))
            logger.info("MCP guide generated successfully: mcp_guide.md")
        except Exception as e:
            logger.error(f"Failed to generate MCP guide: {e}")