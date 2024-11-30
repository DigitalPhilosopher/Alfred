from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable, Any

class AIStrategy(ABC):
    """Abstract base class for AI chat strategies"""
    
    def __init__(self):
        """Initialize strategy with stream callback support"""
        self.on_stream: Optional[Callable[[str], None]] = None
        self.tools: Dict[str, Dict[str, Any]] = {}
    
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

    def set_tools(self, tools: Dict[str, Dict[str, Any]]) -> None:
        """Set the available tools for this strategy"""
        self.tools = tools
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Convert tools dictionary to format expected by LLM APIs"""
        return [
            {
                "name": name,
                "description": tool["description"],
                "input_schema": tool["input_schema"]
            }
            for name, tool in self.tools.items()
        ]