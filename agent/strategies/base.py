from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable

class AIStrategy(ABC):
    """Abstract base class for AI chat strategies"""
    
    def __init__(self):
        """Initialize strategy with stream callback support"""
        self.on_stream: Optional[Callable[[str], None]] = None
    
    @abstractmethod
    def initialize_client(self) -> None:
        """Initialize the API client"""
        pass
    
    @abstractmethod
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Execute chat with the AI model"""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model to use for this strategy"""
        pass
    
    def set_stream_callback(self, callback: Optional[Callable[[str], None]]) -> None:
        """Set the callback function for streaming responses"""
        self.on_stream = callback
    
    def stream_chunk(self, chunk: str) -> None:
        """Safely stream a chunk of text through the callback if it exists"""
        if self.on_stream:
            self.on_stream(chunk)