import os
import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from .manager import BaseMCPManager, BaseMCPManagerError
from .client import BaseMCPClient
from loguru import logger

# Data Models
class RequestForm(BaseModel):
    intent: str = Field('Show me a photo of a cute cat.', description="User's intent or query")
    context: dict = {}

class GenUIRequest(BaseModel):
    intent: str = Field(..., description="User's intent or query")
    context: dict = Field(default_factory=dict, description="Additional context information")
    user_data: str = Field(default="", description="User data to be considered for UI generation")

class ProcessResponse(BaseModel):
    status: str
    intent_received: str
    context_received: Dict[str, Any]
    response: str
    processing_time: float

class GenUIResponse(BaseModel):
    status: str
    intent_received: str
    context_received: Dict[str, Any]
    user_data_received: str
    ui_requirements: str
    processing_time: float

class MCPService:
    """
    Unified MCP Service - dynamically loads configuration based on client path
    Supports both user_client and genui_client configurations
    """
    
    def __init__(self, client_path: str):
        """
        Initialize MCP service with client configuration path
        
        Args:
            client_path: Path to client configuration (e.g., "user_client" or "genui_client")
        """
        self.client_path = client_path
        self.tag = client_path  # Use client_path as tag for logging and yield
        self.service_name = f"MCPService ({client_path})"
        self._initialized = False
        
        # Build paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(current_dir, client_path)
        
        # Validate path exists
        if not os.path.exists(self.config_dir):
            raise BaseMCPManagerError(f"[{self.tag}] Client configuration directory not found: {self.config_dir}")
        
        # Setup manager with auto-detected configuration
        self.mcp_manager = self._create_manager()
        logger.info(f"[{self.tag}] {self.service_name} initialized")
    
    def _create_manager(self) -> BaseMCPManager:
        """Create MCP manager with auto-detected configuration"""
        
        # Auto-detect system prompt file
        system_prompt_candidates = [
            "mcp_client_system_prompt.txt",
            "genui_client_system_prompt.txt",
            "system_prompt.txt"
        ]
        
        system_prompt_path = None
        for candidate in system_prompt_candidates:
            candidate_path = os.path.join(self.config_dir, candidate)
            if os.path.exists(candidate_path):
                system_prompt_path = candidate_path
                break
        
        if not system_prompt_path:
            raise BaseMCPManagerError(f"[{self.tag}] No system prompt file found in {self.config_dir}")
        
        # Create custom manager for this service
        class ServiceMCPManager(BaseMCPManager):
            def __init__(self, config_dir: str, system_prompt_path: str):
                super().__init__(client_class=BaseMCPClient, system_prompt_filename=system_prompt_path)
                self.config_dir = config_dir
            
            async def init_mcp_client(self) -> bool:
                """Initialize MCP client with auto-detected servers"""
                
                # Auto-detect custom servers
                custom_base_dir = os.path.join(self.config_dir, "custom_mcp_servers")
                custom_servers = os.path.exists(custom_base_dir)
                
                # Auto-detect external servers
                external_config_path = os.path.join(self.config_dir, "mcp_servers.json")
                external_servers = os.path.exists(external_config_path)
                
                if not custom_servers and not external_servers:
                    raise BaseMCPManagerError(f"[{self.config_dir}] No server configurations found in {self.config_dir}")
                
                return await super().init_mcp_client(
                    custom_servers=custom_servers,
                    external_servers=external_servers,
                    custom_base_dir=custom_base_dir if custom_servers else None,
                    external_config_path=external_config_path if external_servers else None
                )
        
        return ServiceMCPManager(self.config_dir, system_prompt_path)
    
    async def initialize(self) -> bool:
        """Initialize MCP client connections"""
        if self._initialized:
            return True
            
        try:
            await self.mcp_manager.init_mcp_client()
            await self._post_init_setup()
            self._initialized = True
            logger.info(f"[{self.tag}] {self.service_name} initialization completed successfully")
            return True
        except Exception as e:
            if isinstance(e, BaseMCPManagerError):
                logger.error(f"[{self.tag}] {self.service_name} initialization failed: {str(e)}")
                raise e
            else:
                logger.error(f"[{self.tag}] Unexpected error during {self.service_name} initialization: {str(e)}")
                raise e
    
    async def _post_init_setup(self):
        """Additional setup after MCP client initialization"""
        # Generate MCP guide if manager supports it
        if hasattr(self.mcp_manager, 'generate_mcp_guide'):
            await self.mcp_manager.generate_mcp_guide()
    
    async def cleanup(self):
        """Cleanup MCP client connections"""
        if self._initialized:
            await self.mcp_manager.cleanup_mcp_client()
            self._initialized = False
            logger.info(f"[{self.tag}] {self.service_name} cleanup completed")
    
    @property
    def is_connected(self) -> bool:
        """Check if MCP client is connected"""
        return (self._initialized and self.mcp_manager.is_connected)
    
    async def reconnect(self) -> Dict[str, Any]:
        """Manually reconnect MCP client"""
        try:
            await self.cleanup()
            success = await self.initialize()
            if success:
                return {"status": "success", "message": f"[{self.tag}] {self.service_name} reconnected successfully"}
            else:
                raise BaseMCPManagerError(f"[{self.tag}] Failed to reconnect {self.service_name}")
        except Exception as e:
            logger.error(f"[{self.tag}] Error reconnecting {self.service_name}: {e}")
            raise BaseMCPManagerError(f"[{self.tag}] Error during reconnection: {str(e)}") from e
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools"""
        if not self.is_connected:
            raise BaseMCPManagerError(f"[{self.tag}] {self.service_name} not connected")
        
        try:
            response = await self.mcp_manager.mcp_client_instance.session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in response.tools
            ]
            return {"tools": tools}
        except Exception as e:
            logger.error(f"[{self.tag}] Error listing MCP tools: {e}")
            raise BaseMCPManagerError(f"[{self.tag}] Error retrieving MCP tools: {str(e)}") from e
    
    async def process_request(self, request: dict, model: str, on_update: Any | None = None, multi_agent_expression: Any | None = None) -> Any:
        """
        사용자 요청을 처리하고 도구 실행 결과 리스트를 반환합니다.
        이전의 스트리밍 기반 코드를 대체합니다.
        """
        logger.info(f"[{self.tag}] process_request : {request}")

        if not self.is_connected:
            error_msg = f"[{self.tag}] Error: MCP Client is not connected or available. Please try again later."
            logger.error(error_msg)
            raise BaseMCPManagerError(error_msg)

        try:
            results = await self.mcp_manager.mcp_client_instance.process_query_list(request, model, on_update=on_update, multi_agent_expression=multi_agent_expression)
            return results
        except Exception as e:
            logger.error(f"[{self.tag}] Error in request: {str(e)}")
            raise
    
    # Backward compatibility methods
    async def generate_ui_requirements(self, request: GenUIRequest) -> Any:
        """Generate UI requirements (non-streaming)"""
        request_dict = request.model_dump()
        return await self.process_request(request_dict)
    
    async def list_available_tools(self):
        """List available MCP tools (backward compatibility)"""
        return await self.list_tools()

# Convenience factory functions
def create_user_service() -> MCPService:
    """Create MCP service for user client"""
    return MCPService("user_client")

def create_genui_service() -> MCPService:
    """Create MCP service for genui client"""
    return MCPService("genui_client")

# Backward compatibility aliases
MCPUserService = create_user_service
MCPGenUIService = create_genui_service 