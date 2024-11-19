from anthropic import Anthropic
from typing import List, Dict, Optional
import asyncio
from .base import AIStrategy
from ..logger_config import logger

class AnthropicStrategy(AIStrategy):
    def __init__(self, api_key: str):
        super().__init__()  # Call parent class init
        self.api_key = api_key
        self.client = None
        self.current_stream = None
    
    @property
    def default_model(self) -> str:
        return "claude-3-haiku-20240307"
    
    def initialize_client(self) -> None:
        if not self.client:
            logger.info("Initializing Anthropic client")
            self.client = Anthropic(api_key=self.api_key)
    
    def cancel_current_stream(self):
        if self.current_stream and not self.current_stream.done():
            self.current_stream.cancel()
    
    async def stream_message(self, messages: List[Dict], system: str, model: str):
        try:
            chunks = []
            with self.client.messages.stream(
                model=model,
                max_tokens=1000,
                temperature=0,
                system=system,
                messages=messages
            ) as stream:
                # Regular for loop since text_stream is a regular generator
                for text in stream.text_stream:
                    chunks.append(text)
                    self.stream_chunk(text)  # Use the base class method
                    # Add a small delay to allow for cancellation checks
                    await asyncio.sleep(0)
                    
            return "".join(chunks)
        except asyncio.CancelledError:
            return "".join(chunks) + " (cancelled)"
        except Exception as e:
            logger.error(f"Error in Anthropic stream: {e}", exc_info=True)
            raise
    
    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        try:
            self.initialize_client()
            model = model or self.default_model
            logger.info(f"Starting Anthropic chat with model: {model}")

            # Cancel any existing stream
            if self.current_stream:
                self.cancel_current_stream()

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

            # Set up asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.current_stream = asyncio.ensure_future(
                    self.stream_message(messages, system, model),
                    loop=loop
                )
                return loop.run_until_complete(self.current_stream)
            finally:
                loop.close()

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