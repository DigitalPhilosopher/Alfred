from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
from .strategies import OpenAIStrategy, AnthropicStrategy, AIStrategy
from .logger_config import logger

class AIAgent:
    """Main class that handles AI chat operations using different strategies"""
    
    def __init__(self):
        self.strategy: Optional[AIStrategy] = None
        
    def initialize_strategy(self) -> None:
        """Initialize the appropriate strategy based on available API keys"""
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if anthropic_key and anthropic_key.strip():
            self.strategy = AnthropicStrategy(anthropic_key)
        elif openai_key and openai_key.strip():
            self.strategy = OpenAIStrategy(openai_key)
        else:
            logger.error("No valid API keys found")
            raise ValueError("No valid API keys found for either Anthropic or OpenAI")
    
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """
        Execute chat using the configured strategy
        
        Args:
            prompts: List of message dictionaries with 'role' and 'content' keys
            model: Optional specific model to use
            
        Returns:
            Response text from the AI model
        """
        if not self.strategy:
            self.initialize_strategy()
        
        return self.strategy.chat(prompts, model)