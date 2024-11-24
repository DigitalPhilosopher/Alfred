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
        self.current_tool_calls = {} 
    
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
        self.current_tool_calls = {}  # Store incomplete tool calls
    
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
            current_tool_call = None
            current_json = ""
            
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
                        if hasattr(chunk, 'content_block'):
                            if getattr(chunk.content_block, 'type', None) == 'tool_use':
                                tool_name = chunk.content_block.name
                                current_tool_call = {
                                    'name': tool_name,
                                    'arguments': {},  # Initialize empty dict
                                    'complete': True  # Mark as complete immediately for no-argument tools
                                }
                                logger.info(f"Starting tool call: {tool_name}")
                            elif getattr(chunk.content_block, 'type', None) == 'text':
                                if hasattr(chunk.content_block, 'text') and chunk.content_block.text:
                                    text = chunk.content_block.text
                                    chunks.append(text)
                                    self.stream_chunk(text)
                    
                    elif chunk.type == "content_block_delta":
                        if current_tool_call and hasattr(chunk.delta, 'type') and chunk.delta.type == 'input_json_delta':
                            if hasattr(chunk.delta, 'partial_json'):
                                current_json += chunk.delta.partial_json
                                logger.info(f"Accumulated JSON: {current_json}")
                                
                                # Only try to parse JSON if it's not empty
                                if current_json.strip():
                                    try:
                                        args = json.loads(current_json)
                                        current_tool_call['arguments'] = args
                                        current_tool_call['complete'] = True
                                        logger.info(f"Completed tool arguments: {json.dumps(args, indent=2)}")
                                    except json.JSONDecodeError:
                                        # If JSON is incomplete, continue accumulating
                                        continue
                        elif hasattr(chunk.delta, 'text'):
                            text = chunk.delta.text
                            chunks.append(text)
                            self.stream_chunk(text)
                    
                    elif chunk.type == "content_block_stop":
                        if current_tool_call and current_tool_call['complete']:
                            tool_name = current_tool_call['name']
                            args = current_tool_call['arguments']
                            
                            if tool_name in self.tools:
                                try:
                                    logger.info(f"Executing tool: {tool_name}")
                                    tool_func = self.tools[tool_name]["function"]
                                    
                                    # Execute tool with or without arguments
                                    if asyncio.iscoroutinefunction(tool_func):
                                        result = await tool_func(**args) if args else await tool_func()
                                    else:
                                        result = tool_func(**args) if args else tool_func()
                                    
                                    logger.info(f"Tool {tool_name} executed successfully")
                                    logger.info(f"Tool result: {result}")
                                    
                                    response_text = f"\n{result}"
                                    chunks.append(response_text)
                                    self.stream_chunk(response_text)
                                    
                                except Exception as e:
                                    logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
                                    error_msg = f"\nError executing tool {tool_name}: {str(e)}\n"
                                    chunks.append(error_msg)
                                    self.stream_chunk(error_msg)
                            
                            current_tool_call = None
                            current_json = ""
                            
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