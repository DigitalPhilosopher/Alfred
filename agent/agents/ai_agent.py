from typing import Optional, List, Dict, Callable, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from ..strategies import OpenAIStrategy, AnthropicStrategy, AIStrategy, DummyStrategy
from ..logger_config import logger

class AIAgent(ABC):
    def __init__(self):
        self.strategy: Optional[AIStrategy] = None
        self.on_stream: Optional[Callable[[str], None]] = None
        self.chat_history: List[Dict[str, str]] = []
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.init_chat_history()
        self._register_tools()
        self.env = {}
        self.on_change: Optional[Callable[[object], None]] = None

    def set_change_callback(self, callback: Callable[[object], None]):
        self.on_change = callback
    
    def _register_tools() -> str:
        pass

    def environment_setup(self, env) -> str:
        self.env = env
    
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Return the system prompt for the AI agent.
        Must be implemented by concrete classes.
        
        Returns:
            str: The system prompt that defines the agent's behavior and capabilities
        """
        pass
    
    @abstractmethod
    def init_chat_history(self) -> None:
        """
        Initialize the chat history with system prompt and initial message.
        Must be implemented by concrete classes.
        """
        pass

    def register_tool(self, name: str, func: Callable, description: str, input_schema: Dict[str, Any]) -> None:
        """
        Register a new tool that can be used by the AI agent.
        
        Args:
            name: The name of the tool
            func: The function to be called when the tool is used
            description: A description of what the tool does
            input_schema: JSON schema describing the expected input format
        """
        self.tools[name] = {
            "function": func,
            "description": description,
            "input_schema": input_schema
        }

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
        
        # Pass tools to strategy
        if self.tools and hasattr(self.strategy, 'set_tools'):
            self.strategy.set_tools(self.tools)
    
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