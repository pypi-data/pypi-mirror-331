from dataclasses import dataclass
from typing import Optional, Dict

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
