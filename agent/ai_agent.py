from typing import Optional, List, Dict, Callable
from dotenv import load_dotenv
import os
from .strategies import OpenAIStrategy, AnthropicStrategy, AIStrategy, DummyStrategy
from .logger_config import logger

class AIAgent:
    def __init__(self):
        self.strategy: Optional[AIStrategy] = None
        self.on_stream: Optional[Callable[[str], None]] = None
        self.chat_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! Type your message and press Enter. Press Escape to exit."}
        ]
        
    def initialize_strategy(self) -> None:
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        debug = os.getenv('DEBUG')
        
        if debug == "True":
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

    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the chat history."""
        self.chat_history.append({"role": role, "content": content})

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history

    def chat(self, message: str, model: Optional[str] = None) -> str:
        """Process a single message and return the response."""
        if not self.strategy:
            self.initialize_strategy()
        
        self.add_message("user", message)
        response = self.strategy.chat(self.chat_history, model)
        self.add_message("assistant", response)
        return response