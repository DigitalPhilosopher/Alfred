from anthropic import Anthropic
from typing import List, Dict, Optional, Any
import asyncio
import json
from .base import AIStrategy
from ..logger_config import logger

class AnthropicStrategy(AIStrategy):
    def __init__(self, api_key: str):
        super().__init__()
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
                    logger.info(f"Received chunk type: {chunk.type}")
                    logger.info(f"Received chunk: {chunk}")
                    
                    if chunk.type == "content_block_start":
                        if hasattr(chunk, 'content_block') and getattr(chunk.content_block, 'type', None) == 'tool_use':
                            tool_name = chunk.content_block.name
                            logger.info(f"Processing tool use: {tool_name}")
                            
                            if tool_name in self.tools:
                                try:
                                    # Get tool arguments from input
                                    args = chunk.content_block.input or {}
                                    logger.info(f"Tool arguments: {json.dumps(args, indent=2)}")
                                    
                                    logger.info(f"Executing tool: {tool_name}")
                                    tool_func = self.tools[tool_name]["function"]
                                    
                                    # Handle both async and sync functions
                                    if asyncio.iscoroutinefunction(tool_func):
                                        result = await tool_func(**args)
                                    else:
                                        result = tool_func(**args)
                                    
                                    logger.info(f"Tool {tool_name} executed successfully")
                                    logger.info(f"Tool result: {result}")
                                    
                                    response_text = f"\nTool {tool_name} result: {result}\n"
                                    chunks.append(response_text)
                                    self.stream_chunk(response_text)
                                    
                                except Exception as e:
                                    logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
                                    error_msg = f"\nError executing tool {tool_name}: {str(e)}\n"
                                    chunks.append(error_msg)
                                    self.stream_chunk(error_msg)
                    
                    elif chunk.type == "content_block_delta":
                        if hasattr(chunk.delta, 'value'):
                            text = chunk.delta.value
                        elif hasattr(chunk.delta, 'text'):
                            text = chunk.delta.text
                        else:
                            text = str(chunk.delta)
                        
                        chunks.append(text)
                        self.stream_chunk(text)
                        
                    await asyncio.sleep(0)
            
            return "".join(chunks)
            
        except Exception as e:
            logger.error(f"Error in Anthropic stream: {e}", exc_info=True)
            raise

    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        try:
            self.initialize_client()
            model = model or self.default_model
            logger.info(f"Starting Anthropic chat with model: {model}")

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