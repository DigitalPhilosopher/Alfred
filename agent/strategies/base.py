from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AIStrategy(ABC):
    """Abstract base class for AI chat strategies"""
    
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