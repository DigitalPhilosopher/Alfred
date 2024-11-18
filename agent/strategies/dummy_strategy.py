from typing import List, Dict, Optional
from .base import AIStrategy
from time import sleep

class DummyStrategy(AIStrategy):
    def __init__(self, api_key: str):
        pass

    def initialize_client(self) -> None:
        """Initialize the API client"""
        pass
    
    @property
    def default_model(self) -> str:
        """Default model to use for this strategy"""
        pass
    
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        sleep(2)
        return "Dummy answer"