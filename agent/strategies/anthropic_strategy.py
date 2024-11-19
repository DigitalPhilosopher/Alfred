from anthropic import Anthropic
from typing import List, Dict, Optional, Any
import asyncio
import json
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
        return "claude-3-5-sonnet-20241022"
    
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
            kwargs = {
                "model": model,
                "max_tokens": 1000,
                "temperature": 0,
                "system": system,
                "messages": messages
            }
            
            # Add tools if available
            if self.tools:
                kwargs["tools"] = self.get_tool_definitions()
            
            with self.client.messages.stream(**kwargs) as stream:
                for chunk in stream:
                    if chunk.type == "message_start":
                        continue
                    elif chunk.type == "content_block_start":
                        continue
                    elif chunk.type == "tool_calls":
                        # Execute tool calls
                        for tool_call in chunk.tool_calls:
                            tool_name = tool_call.name
                            if tool_name in self.tools:
                                try:
                                    args = json.loads(tool_call.arguments)
                                    result = self.tools[tool_name]["function"](**args)
                                    chunks.append(f"\nTool {tool_name} result: {result}\n")
                                    self.stream_chunk(f"\nTool {tool_name} result: {result}\n")
                                except Exception as e:
                                    error_msg = f"\nError executing tool {tool_name}: {str(e)}\n"
                                    chunks.append(error_msg)
                                    self.stream_chunk(error_msg)
                    elif chunk.type == "content_block_delta":
                        chunks.append(chunk.delta.text)
                        self.stream_chunk(chunk.delta.text)
                    
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