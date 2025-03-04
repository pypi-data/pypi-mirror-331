import aiohttp
import asyncio
from typing import Optional, Dict, AsyncGenerator, Any

from .base import BaseSubmodule
from ..models import SandboxResponse, StreamEvent

class CodeModule(BaseSubmodule):
    """Code execution operations for the sandbox environment.
    
    This module provides methods for executing Python code in the sandbox.
    """
    
    async def execute(
        self,
        code: str,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> SandboxResponse:
        """Execute Python code in the sandbox.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            environment: Optional environment variables for the execution
            
        Returns:
            SandboxResponse containing execution results
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
            
        headers = self._get_headers()
        
        data = {
            "code": code,
            "timeout": timeout
        }
        
        if environment:
            data["environment"] = environment
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/execute",
                    headers=headers,
                    json=data
                ) as response:
                    return await self._handle_response(response)
                    
        except Exception as e:
            return SandboxResponse(success=False, error=f"Connection error: {str(e)}")
    
    async def execute_stream(
        self,
        code: str,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute Python code in the sandbox with streaming output.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            environment: Optional environment variables for the execution
            
        Yields:
            StreamEvent objects containing execution output
        """
        ready = await self._ensure_ready()
        if not ready.success:
            yield StreamEvent(type="error", data=ready.error or "Sandbox not ready")
            return
            
        headers = self._get_headers()
        
        data = {
            "code": code,
            "timeout": timeout
        }
        
        if environment:
            data["environment"] = environment
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/execute/stream",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield StreamEvent(type="error", data=error_text)
                        return
                    
                    # Process the streaming response
                    async for line in response.content:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            event_data = line.decode('utf-8')
                            # Check if it's a JSON object
                            if event_data.startswith('{') and event_data.endswith('}'):
                                import json
                                event_json = json.loads(event_data)
                                event_type = event_json.get('type', 'info')
                                event_data = event_json.get('data', '')
                                yield StreamEvent(type=event_type, data=event_data)
                                
                                # If execution is complete, break the loop
                                if event_type == 'completed':
                                    break
                            else:
                                # Treat as stdout if not JSON
                                yield StreamEvent(type="stdout", data=event_data)
                        except Exception as e:
                            yield StreamEvent(type="error", data=f"Failed to parse event: {str(e)}")
                            break
                                
        except Exception as e:
            yield StreamEvent(type="error", data=f"Connection error: {str(e)}")
    
    async def execute_file(
        self,
        file_path: str,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> SandboxResponse:
        """Execute a Python file in the sandbox.
        
        Args:
            file_path: Path to the Python file in the sandbox
            timeout: Maximum execution time in seconds
            environment: Optional environment variables for the execution
            
        Returns:
            SandboxResponse containing execution results
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
            
        # Execute code to check if the file exists and is a Python file
        check_code = f"""
import os

file_path = "{file_path}"
if not os.path.exists(file_path):
    result = {{"success": False, "error": f"File not found: {{file_path}}"}}
elif not os.path.isfile(file_path):
    result = {{"success": False, "error": f"Not a file: {{file_path}}"}}
elif not file_path.endswith('.py'):
    result = {{"success": False, "error": f"Not a Python file: {{file_path}}"}}
else:
    result = {{"success": True}}

result
"""
        check_response = await self.execute(check_code)
        if not check_response.success:
            return check_response
            
        result = check_response.data.get('result', {})
        if not result.get('success', False):
            return SandboxResponse(
                success=False,
                error=result.get('error', 'Unknown error checking file')
            )
            
        # Execute the Python file
        headers = self._get_headers()
        
        data = {
            "file_path": file_path,
            "timeout": timeout
        }
        
        if environment:
            data["environment"] = environment
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/execute",
                    headers=headers,
                    json=data
                ) as response:
                    return await self._handle_response(response)
                    
        except Exception as e:
            return SandboxResponse(success=False, error=f"Connection error: {str(e)}")
    
    async def execute_file_stream(
        self,
        file_path: str,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute a Python file in the sandbox with streaming output.
        
        Args:
            file_path: Path to the Python file in the sandbox
            timeout: Maximum execution time in seconds
            environment: Optional environment variables for the execution
            
        Yields:
            StreamEvent objects containing execution output
        """
        ready = await self._ensure_ready()
        if not ready.success:
            yield StreamEvent(type="error", data=ready.error or "Sandbox not ready")
            return
            
        # Execute code to check if the file exists and is a Python file
        check_code = f"""
import os

file_path = "{file_path}"
if not os.path.exists(file_path):
    result = {{"success": False, "error": f"File not found: {{file_path}}"}}
elif not os.path.isfile(file_path):
    result = {{"success": False, "error": f"Not a file: {{file_path}}"}}
elif not file_path.endswith('.py'):
    result = {{"success": False, "error": f"Not a Python file: {{file_path}}"}}
else:
    result = {{"success": True}}

result
"""
        check_response = await self.execute(check_code)
        if not check_response.success:
            yield StreamEvent(type="error", data=check_response.error or "Failed to check file")
            return
            
        result = check_response.data.get('result', {})
        if not result.get('success', False):
            yield StreamEvent(type="error", data=result.get('error', 'Unknown error checking file'))
            return
            
        # Execute the Python file with streaming output
        headers = self._get_headers()
        
        data = {
            "file_path": file_path,
            "timeout": timeout
        }
        
        if environment:
            data["environment"] = environment
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/execute/file/stream",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield StreamEvent(type="error", data=error_text)
                        return
                    
                    # Process the streaming response
                    async for line in response.content:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            event_data = line.decode('utf-8')
                            # Check if it's a JSON object
                            if event_data.startswith('{') and event_data.endswith('}'):
                                import json
                                event_json = json.loads(event_data)
                                event_type = event_json.get('type', 'info')
                                event_data = event_json.get('data', '')
                                yield StreamEvent(type=event_type, data=event_data)
                                
                                # If execution is complete, break the loop
                                if event_type == 'completed':
                                    break
                            else:
                                # Treat as stdout if not JSON
                                yield StreamEvent(type="stdout", data=event_data)
                        except Exception as e:
                            yield StreamEvent(type="error", data=f"Failed to parse event: {str(e)}")
                            break
                                
        except Exception as e:
            yield StreamEvent(type="error", data=f"Connection error: {str(e)}")
