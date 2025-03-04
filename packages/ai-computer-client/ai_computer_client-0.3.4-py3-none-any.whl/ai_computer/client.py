import aiohttp
import json
import asyncio
from typing import Optional, Dict, AsyncGenerator, Union, List, BinaryIO
from dataclasses import dataclass
import os
import mimetypes
from pathlib import Path
import logging

from .models import SandboxResponse, StreamEvent, FileOperationResponse
from .submodules import FileSystemModule, ShellModule, CodeModule

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class SandboxResponse:
    """Response from sandbox operations.
    
    Attributes:
        success: Whether the operation was successful
        data: Optional response data
        error: Optional error message if operation failed
    """
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class StreamEvent:
    """Event from streaming code execution.
    
    Attributes:
        type: Type of event ('stdout', 'stderr', 'info', 'error', 'completed', 'keepalive')
        data: Event data
    """
    type: str
    data: str

@dataclass
class FileOperationResponse:
    """Response from file operations.
    
    Attributes:
        success: Whether the operation was successful
        filename: Name of the file
        size: Size of the file in bytes
        path: Path where the file was saved
        message: Optional status message
        error: Optional error message if operation failed
    """
    success: bool
    filename: Optional[str] = None
    size: Optional[int] = None
    path: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class SandboxClient:
    """Client for interacting with the AI Sandbox service.
    
    This client provides methods to execute Python code in an isolated sandbox environment.
    It handles authentication, sandbox creation/deletion, and code execution.
    
    The client is organized into submodules for different types of operations:
    - fs: File system operations (upload, download, read, write)
    - shell: Shell command execution
    - code: Python code execution
    
    Args:
        base_url: The base URL of the sandbox service
        token: Optional pre-existing authentication token
    """
    
    def __init__(
        self,
        base_url: str = "http://api.aicomputer.dev",
        token: Optional[str] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.sandbox_id = None
        
        # Initialize submodules
        self._fs = FileSystemModule(self)
        self._shell = ShellModule(self)
        self._code = CodeModule(self)
        
    @property
    def fs(self) -> FileSystemModule:
        """File system operations submodule."""
        return self._fs
        
    @property
    def shell(self) -> ShellModule:
        """Shell operations submodule."""
        return self._shell
        
    @property
    def code(self) -> CodeModule:
        """Code execution operations submodule."""
        return self._code
        
    async def setup(self) -> SandboxResponse:
        """Initialize the client and create a sandbox.
        
        This method:
        1. Gets a development token (if not provided)
        2. Creates a new sandbox
        3. Waits for the sandbox to be ready
        
        Returns:
            SandboxResponse indicating success/failure
        """
        async with aiohttp.ClientSession() as session:
            # Get development token if not provided
            if not self.token:
                async with session.post(f"{self.base_url}/dev/token") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.token = data["access_token"]
                    else:
                        text = await response.text()
                        return SandboxResponse(success=False, error=text)
                
            # Create sandbox
            headers = {"Authorization": f"Bearer {self.token}"}
            async with session.post(f"{self.base_url}/api/v1/sandbox/create", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.sandbox_id = data["sandbox_id"]
                else:
                    text = await response.text()
                    return SandboxResponse(success=False, error=text)
                
            # Wait for sandbox to be ready
            return await self.wait_for_ready()
    
    async def wait_for_ready(self, max_attempts: int = 10, delay: float = 1.0) -> SandboxResponse:
        """Wait for the sandbox to be ready.
        
        Args:
            max_attempts: Maximum number of attempts to check status
            delay: Delay between attempts in seconds
            
        Returns:
            SandboxResponse with success=True if sandbox is ready
        """
        if not self.sandbox_id:
            return SandboxResponse(
                success=False,
                error="Sandbox ID not set. Call setup() first."
            )
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Checking sandbox status (attempt {attempt + 1}/{max_attempts})...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/status",
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            # If we get an error, wait and try again
                            logger.debug(f"Waiting {delay}s before next attempt...")
                            await asyncio.sleep(delay)
                            continue
                            
                        data = await response.json()
                        status = data.get("status", "").lower()
                        logger.debug(f"Current sandbox status: {status}")
                        
                        # Check for both 'ready' and 'running' status as indicators that the sandbox is ready
                        if status == "ready" or status == "running":
                            return SandboxResponse(success=True, data=data)
                        elif status == "error":
                            return SandboxResponse(
                                success=False,
                                error=data.get("error", "Unknown error initializing sandbox")
                            )
                        
                        # If not ready yet, wait and try again
                        logger.debug(f"Waiting {delay}s before next attempt...")
                        await asyncio.sleep(delay)
                        
            except Exception as e:
                # If we get an exception, wait and try again
                logger.error(f"Error checking sandbox status: {str(e)}")
                await asyncio.sleep(delay)
                
        return SandboxResponse(
            success=False,
            error=f"Sandbox not ready after {max_attempts} attempts"
        )
    
    async def cleanup(self) -> SandboxResponse:
        """Delete the sandbox.
        
        Returns:
            SandboxResponse indicating success/failure
        """
        if not self.token or not self.sandbox_id:
            return SandboxResponse(success=False, error="Client not properly initialized. Call setup() first")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        return SandboxResponse(success=False, error=text)
                    
                    # Reset sandbox ID
                    self.sandbox_id = None
                    return SandboxResponse(success=True)
                    
        except Exception as e:
            return SandboxResponse(success=False, error=f"Connection error: {str(e)}")
    
    # Backward compatibility methods
    
    async def execute_code(self, code: str, timeout: int = 30) -> SandboxResponse:
        """Execute Python code in the sandbox.
        
        This is a backward compatibility method that delegates to the code submodule.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            SandboxResponse containing execution results
        """
        return await self.code.execute(code, timeout)
    
    async def execute_code_stream(self, code: str, timeout: int = 30) -> AsyncGenerator[StreamEvent, None]:
        """Execute Python code in the sandbox with streaming output.
        
        This is a backward compatibility method that delegates to the code submodule.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            
        Yields:
            StreamEvent objects containing execution output
        """
        async for event in self.code.execute_stream(code, timeout):
            yield event
    
    async def execute_shell(self, command: str, args: Optional[List[str]] = None, timeout: int = 30) -> SandboxResponse:
        """Execute a shell command in the sandbox.
        
        This is a backward compatibility method that delegates to the shell submodule.
        
        Args:
            command: The shell command to execute
            args: Optional list of arguments for the command
            timeout: Maximum execution time in seconds
            
        Returns:
            SandboxResponse containing execution results
        """
        return await self.shell.execute(command, args, timeout)
    
    async def upload_file(
        self,
        file_path: Union[str, Path],
        destination: str = "/workspace",
        chunk_size: int = 1024 * 1024,
        timeout: int = 300
    ) -> FileOperationResponse:
        """Upload a file to the sandbox environment.
        
        This is a backward compatibility method that delegates to the fs submodule.
        
        Args:
            file_path: Path to the file to upload
            destination: Destination path in the sandbox (absolute path starting with /)
            chunk_size: Size of chunks for reading large files
            timeout: Maximum upload time in seconds
            
        Returns:
            FileOperationResponse containing upload results
        """
        return await self.fs.upload_file(file_path, destination, chunk_size, timeout)
    
    async def download_file(
        self,
        remote_path: str,
        local_path: Optional[Union[str, Path]] = None,
        timeout: int = 300
    ) -> FileOperationResponse:
        """Download a file from the sandbox.
        
        This is a backward compatibility method that delegates to the fs submodule.
        
        Args:
            remote_path: Path to the file in the sandbox
            local_path: Local path to save the file (if None, uses the filename from remote_path)
            timeout: Maximum download time in seconds
            
        Returns:
            FileOperationResponse containing download results
        """
        return await self.fs.download_file(remote_path, local_path, timeout)
    
    async def upload_bytes(
        self,
        content: Union[bytes, BinaryIO],
        filename: str,
        destination: str = "/workspace",
        content_type: Optional[str] = None,
        timeout: int = 300
    ) -> FileOperationResponse:
        """Upload bytes or a file-like object to the sandbox environment.
        
        This is a backward compatibility method that delegates to the fs submodule.
        
        Args:
            content: Bytes or file-like object to upload
            filename: Name to give the file in the sandbox
            destination: Destination path in the sandbox (absolute path starting with /)
            content_type: Optional MIME type (will be guessed from filename if not provided)
            timeout: Maximum upload time in seconds
            
        Returns:
            FileOperationResponse containing upload results
        """
        # Create a temporary file with the content
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            if isinstance(content, bytes):
                temp_file.write(content)
            else:
                # Ensure we're at the start of the file
                if hasattr(content, 'seek'):
                    content.seek(0)
                # Read and write in chunks to handle large files
                chunk = content.read(1024 * 1024)  # 1MB chunks
                while chunk:
                    temp_file.write(chunk)
                    chunk = content.read(1024 * 1024)
        
        try:
            # Upload the temporary file
            temp_path = Path(temp_file.name)
            result = await self.fs.upload_file(
                file_path=temp_path,
                destination=os.path.join(destination, filename),
                timeout=timeout
            )
            
            # If successful, update the filename in the response
            if result.success:
                result.filename = filename
            
            return result
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    async def download_bytes(self, remote_path: str, timeout: Optional[float] = None) -> Union[bytes, FileOperationResponse]:
        """
        Download a file from the sandbox into memory.

        Args:
            remote_path: Path to the file in the sandbox.
            timeout: Timeout in seconds for the operation.

        Returns:
            bytes: The file contents as bytes if successful.
            FileOperationResponse: On failure, returns a FileOperationResponse with error details.
        """
        await self.wait_for_ready()
        
        try:
            response = await self.fs.download_bytes(remote_path, timeout=timeout or 300)
            if response.success:
                return response.data.get('content')
            else:
                return FileOperationResponse(
                    success=False,
                    error=response.error or "Failed to download file"
                )
        except Exception as e:
            return FileOperationResponse(
                success=False,
                error=f"Error downloading file: {str(e)}"
            )
    
    # Additional backward compatibility methods can be added as needed