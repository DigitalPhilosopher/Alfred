from typing import Optional, List, Dict, Callable
from dotenv import load_dotenv
import os
from .strategies import OpenAIStrategy, AnthropicStrategy, AIStrategy, DummyStrategy
from .logger_config import logger

class AIAgent:
    def __init__(self):
        self.strategy: Optional[AIStrategy] = None
        self.on_stream: Optional[Callable[[str], None]] = None
        
    def initialize_strategy(self) -> None:
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        debug = os.getenv('DEBUG')
        
        if debug:
            self.strategy = DummyStrategy("")
        elif anthropic_key and anthropic_key.strip():
            self.strategy = AnthropicStrategy(anthropic_key)
        elif openai_key and openai_key.strip():
            self.strategy = OpenAIStrategy(openai_key)
        else:
            logger.error("No valid API keys found")
            raise ValueError("No valid API keys found for either Anthropic or OpenAI")
        
        if hasattr(self.strategy, 'on_stream'):
            self.strategy.on_stream = self.on_stream
    
    def set_stream_callback(self, callback: Callable[[str], None]):
        self.on_stream = callback
        if self.strategy and hasattr(self.strategy, 'on_stream'):
            self.strategy.on_stream = callback

    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.strategy:
            self.initialize_strategy()
        
        return self.strategy.chat(prompts, model)