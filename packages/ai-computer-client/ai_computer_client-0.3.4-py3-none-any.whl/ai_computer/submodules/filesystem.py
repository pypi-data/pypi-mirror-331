import aiohttp
import asyncio
import os
import mimetypes
from pathlib import Path
from typing import Optional, Union, BinaryIO, Dict, Any
from urllib.parse import quote

from .base import BaseSubmodule
from ..models import FileOperationResponse, SandboxResponse

class FileSystemModule(BaseSubmodule):
    """File system operations for the sandbox environment.
    
    This module provides methods for file operations such as uploading,
    downloading, reading, and writing files in the sandbox.
    """
    
    async def upload_file(
        self,
        file_path: Union[str, Path],
        destination: str = "/workspace",
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        timeout: int = 300  # 5 minutes
    ) -> FileOperationResponse:
        """Upload a file to the sandbox environment.
        
        Args:
            file_path: Path to the file to upload
            destination: Destination path in the sandbox (absolute path starting with /)
            chunk_size: Size of chunks for reading large files
            timeout: Maximum upload time in seconds
            
        Returns:
            FileOperationResponse containing upload results
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return FileOperationResponse(
                success=False,
                error=ready.error or "Sandbox not ready"
            )

        # Convert to Path object and validate file
        file_path = Path(file_path)
        if not file_path.exists():
            return FileOperationResponse(
                success=False,
                error=f"File not found: {file_path}"
            )
        
        if not file_path.is_file():
            return FileOperationResponse(
                success=False,
                error=f"Not a file: {file_path}"
            )

        # Get file size and validate
        file_size = file_path.stat().st_size
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return FileOperationResponse(
                success=False,
                error="File too large. Maximum size is 100MB"
            )

        try:
            # Prepare the upload
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            # Guess content type
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file',
                         open(file_path, 'rb'),  # Pass file object directly for streaming
                         filename=file_path.name,
                         content_type=content_type)
            data.add_field('path', destination)

            timeout_settings = aiohttp.ClientTimeout(
                total=timeout,
                connect=30,
                sock_connect=30,
                sock_read=timeout
            )

            async with aiohttp.ClientSession(timeout=timeout_settings) as session:
                async with session.post(
                    f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/files/upload",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return FileOperationResponse(
                            success=False,
                            error=f"Upload failed: {error_text}"
                        )

                    result = await response.json()
                    return FileOperationResponse(
                        success=True,
                        filename=result.get("filename"),
                        size=result.get("size"),
                        path=result.get("path"),
                        message=result.get("message")
                    )

        except asyncio.TimeoutError:
            return FileOperationResponse(
                success=False,
                error=f"Upload timed out after {timeout} seconds"
            )
        except Exception as e:
            return FileOperationResponse(
                success=False,
                error=f"Upload failed: {str(e)}"
            )
    
    async def download_file(
        self,
        remote_path: str,
        local_path: Optional[str] = None,
        timeout: int = 300
    ) -> FileOperationResponse:
        """Download a file from the sandbox to the local filesystem.
        
        Args:
            remote_path: Path to the file in the sandbox
            local_path: Local path to save the file (defaults to basename of remote_path)
            timeout: Maximum download time in seconds
            
        Returns:
            FileOperationResponse containing download results
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return FileOperationResponse(
                success=False,
                error=ready.error
            )
            
        # Determine local path if not provided
        if local_path is None:
            local_path = os.path.basename(remote_path)
        local_path = Path(local_path)
        
        # Create parent directories if they don't exist
        os.makedirs(local_path.parent, exist_ok=True)
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        # Store original path for error messages
        original_path = remote_path
        
        # Ensure path is absolute
        if not remote_path.startswith('/'):
            remote_path = f"/{remote_path}"
        
        timeout_settings = aiohttp.ClientTimeout(
            total=timeout,
            connect=30,
            sock_connect=30,
            sock_read=timeout
        )
        
        try:
            async with aiohttp.ClientSession(timeout=timeout_settings) as session:
                # Use the new API endpoint with query parameters
                url = f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/files"
                params = {"path": quote(remote_path)}
                
                async with session.get(
                    url,
                    headers=headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return FileOperationResponse(
                            success=False,
                            error=f"Failed to download file '{original_path}': {error_text}"
                        )
                    
                    # Get content disposition header to extract filename
                    content_disposition = response.headers.get('Content-Disposition', '')
                    filename = os.path.basename(remote_path)  # Default to basename of remote path
                    
                    # Extract filename from content disposition if available
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"\'')
                    
                    # Save the file
                    with open(local_path, 'wb') as f:
                        size = 0
                        async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                            f.write(chunk)
                            size += len(chunk)
                    
                    return FileOperationResponse(
                        success=True,
                        filename=filename,
                        size=size,
                        path=str(local_path),
                        message=f"File downloaded successfully to {local_path}"
                    )
                    
        except asyncio.TimeoutError:
            # Clean up partial download
            if local_path.exists():
                local_path.unlink()
            return FileOperationResponse(
                success=False,
                error=f"Download timed out after {timeout} seconds"
            )
        except Exception as e:
            # Clean up partial download
            if local_path.exists():
                local_path.unlink()
            return FileOperationResponse(
                success=False,
                error=f"Download failed: {str(e)}"
            )
    
    async def read_file(self, path: str, encoding: Optional[str] = 'utf-8') -> SandboxResponse:
        """Read a file from the sandbox.
        
        Args:
            path: Path to the file in the sandbox
            encoding: Text encoding to use (None for binary)
            
        Returns:
            SandboxResponse with the file content
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
            
        # Ensure path is absolute
        if not path.startswith('/'):
            path = f"/{path}"
            
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use the new API endpoint with query parameters
                url = f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/files"
                params = {"path": quote(path)}
                
                async with session.get(
                    url,
                    headers=headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return SandboxResponse(
                            success=False,
                            error=f"Failed to read file: {error_text}"
                        )
                    
                    # Read the content
                    content = await response.read()
                    size = len(content)
                    
                    # Decode if needed
                    if encoding is not None:
                        try:
                            content = content.decode(encoding)
                        except UnicodeDecodeError:
                            return SandboxResponse(
                                success=False,
                                error=f"Failed to decode file with encoding {encoding}"
                            )
                    
                    return SandboxResponse(
                        success=True,
                        data={
                            'content': content,
                            'size': size
                        }
                    )
                    
        except Exception as e:
            return SandboxResponse(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )
    
    async def write_file(
        self, 
        path: str, 
        content: Union[str, bytes],
        encoding: str = 'utf-8'
    ) -> SandboxResponse:
        """Write content to a file in the sandbox.
        
        Args:
            path: Path to the file in the sandbox
            content: Content to write (string or bytes)
            encoding: Text encoding to use (ignored for bytes content)
            
        Returns:
            SandboxResponse indicating success or failure
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
        
        # Convert string to bytes if needed
        if isinstance(content, str):
            try:
                content = content.encode(encoding)
            except UnicodeEncodeError:
                return SandboxResponse(
                    success=False,
                    error=f"Failed to encode content with encoding {encoding}"
                )
        
        # Ensure path is absolute and normalize any double slashes
        if not path.startswith('/'):
            path = f"/{path}"
        clean_path = '/'.join(part for part in path.split('/') if part)
        clean_path = f"/{clean_path}"
        
        # Extract the filename and destination directory
        filename = os.path.basename(path)
        destination = os.path.dirname(path)
        
        # Create a temporary file with the content
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp_file.write(content)
            temp_file.close()
            
            # Upload the temporary file
            result = await self.upload_file(
                file_path=temp_file.name,
                destination=destination
            )
            
            if result.success:
                return SandboxResponse(
                    success=True,
                    data={
                        'path': result.path,
                        'size': result.size
                    }
                )
            else:
                return SandboxResponse(
                    success=False,
                    error=f"Failed to write file: {result.error}"
                )
        except Exception as e:
            return SandboxResponse(
                success=False,
                error=f"Failed to write file: {str(e)}"
            )
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    async def download_bytes(self, path: str, timeout: int = 300) -> SandboxResponse:
        """Download a file from the sandbox into memory.
        
        Args:
            path: Path to the file in the sandbox
            timeout: Maximum download time in seconds
            
        Returns:
            SandboxResponse with the file content as bytes in the data field
        """
        ready = await self._ensure_ready()
        if not ready.success:
            return ready
            
        # Ensure path is absolute
        if not path.startswith('/'):
            path = f"/{path}"
            
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        timeout_settings = aiohttp.ClientTimeout(
            total=timeout,
            connect=30,
            sock_connect=30,
            sock_read=timeout
        )
        
        try:
            async with aiohttp.ClientSession(timeout=timeout_settings) as session:
                # Use the new API endpoint with query parameters
                url = f"{self.base_url}/api/v1/sandbox/{self.sandbox_id}/files"
                params = {"path": quote(path)}
                
                async with session.get(
                    url,
                    headers=headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return SandboxResponse(
                            success=False,
                            error=f"Download failed: {error_text}"
                        )
                    
                    # Read the content
                    content = await response.read()
                    size = len(content)
                    
                    return SandboxResponse(
                        success=True,
                        data={
                            'content': content,
                            'size': size
                        }
                    )
                    
        except Exception as e:
            return SandboxResponse(
                success=False,
                error=f"Failed to download file: {str(e)}"
            )

