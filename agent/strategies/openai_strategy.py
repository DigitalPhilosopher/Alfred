import openai
from typing import List, Dict, Optional
from .base import AIStrategy
from ..logger_config import logger

class OpenAIStrategy(AIStrategy):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
    
    @property
    def default_model(self) -> str:
        return "gpt-4-turbo-preview"
    
    def initialize_client(self) -> None:
        if not self.client:
            logger.info("Initializing OpenAI client")
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        try:
            self.initialize_client()
            model = model or self.default_model
            logger.info(f"Starting OpenAI chat with model: {model}")
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
            ]
            messages.extend(prompts)
            
            logger.debug(f"Sending request to OpenAI with {len(messages)} messages")
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            
            logger.info("Successfully received OpenAI response")
            return response.choices[0].message.content
            
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e.__cause__}")
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error {e.status_code}: {e.response}")
            raise
        except openai.APIStatusError as e:
            logger.error(f"OpenAI status error {e.status_code}: {e.response}")
            raise
        except openai.BadRequestError as e:
            logger.error(f"OpenAI bad request error {e.status_code}: {e.response}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI chat: {e}", exc_info=True)
            raise