from typing import Optional, Dict, Any
import aiohttp
from ..models import SandboxResponse

class BaseSubmodule:
    """Base class for all submodules.
    
    This class provides common functionality for all submodules, including
    access to the parent client's authentication token and sandbox ID.
    
    Attributes:
        _client: Reference to the parent SandboxClient
    """
    
    def __init__(self, client):
        """Initialize the submodule.
        
        Args:
            client: The parent SandboxClient instance
        """
        self._client = client
    
    @property
    def base_url(self) -> str:
        """Get the base URL from the parent client."""
        return self._client.base_url
    
    @property
    def token(self) -> Optional[str]:
        """Get the authentication token from the parent client."""
        return self._client.token
    
    @property
    def sandbox_id(self) -> Optional[str]:
        """Get the sandbox ID from the parent client."""
        return self._client.sandbox_id
    
    async def _ensure_ready(self) -> SandboxResponse:
        """Ensure the sandbox is ready for operations.
        
        Returns:
            SandboxResponse indicating if the sandbox is ready
        """
        if not self.token or not self.sandbox_id:
            return SandboxResponse(
                success=False, 
                error="Client not properly initialized. Call setup() first"
            )
        
        # Ensure sandbox is ready
        return await self._client.wait_for_ready()
    
    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Get the headers for API requests.
        
        Args:
            content_type: The content type for the request
            
        Returns:
            Dictionary of headers
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": content_type
        }
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> SandboxResponse:
        """Handle the API response.
        
        Args:
            response: The aiohttp response object
            
        Returns:
            SandboxResponse with the parsed response data
        """
        if response.status != 200:
            error_text = await response.text()
            return SandboxResponse(success=False, error=error_text)
        
        result = await response.json()
        return SandboxResponse(success=True, data=result)
