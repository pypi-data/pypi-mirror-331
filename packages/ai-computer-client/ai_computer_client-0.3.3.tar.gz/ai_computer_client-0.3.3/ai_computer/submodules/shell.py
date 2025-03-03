import aiohttp
import asyncio
from typing import Optional, List, Dict, Any

from .base import BaseSubmodule
from ..models import SandboxResponse, StreamEvent

class ShellModule(BaseSubmodule):
    """Shell command execution for the sandbox environment.
    
    This module provides methods for executing shell commands in the sandbox.
    """
    
    async def execute(
        self,
        command: str,
        args: Optional[List[str]] = None,
        timeout: int = 30
    ) -> SandboxResponse:
        """Execute a shell command in the sandbox.
        
        Args:
            command: The shell command to execute
            args: Optional list of arguments for the command
            timeout: Maximum execution time in seconds
            
        Returns:
            SandboxResponse containing execution results
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
            
        headers = self._get_headers()
        
        data = {
            "command": command,
            "args": args or [],
            "timeout": timeout
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/execute/shell",
                    headers=headers,
                    json=data
                ) as response:
                    return await self._handle_response(response)
                    
        except Exception as e:
            return SandboxResponse(success=False, error=f"Connection error: {str(e)}")
