from anthropic import Anthropic
from typing import List, Dict, Optional
from .base import AIStrategy
from ..logger_config import logger

class AnthropicStrategy(AIStrategy):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
    
    @property
    def default_model(self) -> str:
        return "claude-3-haiku-20240307"
    
    def initialize_client(self) -> None:
        if not self.client:
            logger.info("Initializing Anthropic client")
            self.client = Anthropic(api_key=self.api_key)
    
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        try:
            self.initialize_client()
            model = model or self.default_model
            logger.info(f"Starting Anthropic chat with model: {model}")

            system = "You are a helpful assistant."
            messages = []
            
            for prompt in prompts:
                if prompt["role"] == "system":
                    system = prompt["content"]
                else:
                    messages.append({
                        "role": prompt["role"],
                        "content": [
                            {
                                "type": "text",
                                "text": prompt["content"]
                            }
                        ]
                    })

            message = self.client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0,
                system=system,
                messages=messages
            )

            logger.info("Successfully received Anthropic response")
            return message.content[0].text

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.error(f"Anthropic rate limit error: {e}")
            elif "status" in str(e).lower():
                logger.error(f"Anthropic status error: {e}")
            elif "bad_request" in str(e).lower():
                logger.error(f"Anthropic bad request error: {e}")
            else:
                logger.error(f"Unexpected error in Anthropic chat: {e}", exc_info=True)
            raise