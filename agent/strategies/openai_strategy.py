import openai
from typing import List, Dict, Optional
from .base import AIStrategy
from ..logger_config import logger
from concurrent.futures import CancelledError
import asyncio
import json

class OpenAIStrategy(AIStrategy):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.client = None
        self.current_task = None
    
    @property
    def default_model(self) -> str:
        return "gpt-4-turbo-preview"
    
    def initialize_client(self) -> None:
        if not self.client:
            logger.info("Initializing OpenAI client")
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def cancel_current_stream(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
    
    async def stream_message(self, messages: List[Dict[str, str]], model: str, callback):
        try:
            self.initialize_client()
            logger.info(f"Starting OpenAI streaming chat with model: {model}")
            
            # Prepare kwargs with optional tools
            kwargs = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            
            # Add tools if available
            if self.tools:
                kwargs["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": name,
                            "description": tool["description"],
                            "parameters": tool["input_schema"]
                        }
                    }
                    for name, tool in self.tools.items()
                ]
            
            # Create the stream with tools
            stream = self.client.chat.completions.create(**kwargs)
            
            full_response = []
            # Process the synchronous stream in chunks
            for chunk in stream:
                if asyncio.current_task().cancelled():
                    raise asyncio.CancelledError()
                
                # Handle tool calls
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'tool_calls'):
                    tool_calls = chunk.choices[0].delta.tool_calls
                    logger.info(f"Tool calls: {tool_calls}")
                    if tool_calls:
                        logger.info(f"Processing tool calls: {tool_calls}")
                        for tool_call in tool_calls:
                            logger.info(f"Processing tool call: {tool_call}")
                            if tool_call.function.name in self.tools:
                                logger.info(f"Tool {tool_call.function.name} found in tools")
                                try:
                                    # Parse and execute tool
                                    tool_name = tool_call.function.name
                                    logger.info(f"Tool name: {tool_name}")
                                    args = json.loads(tool_call.function.arguments or '{}')
                                    logger.info(f"Tool arguments: {args}")
                                    tool_func = self.tools[tool_name]["function"]
                                    logger.info(f"Tool function: {tool_func}")
                                    
                                    # Handle both async and sync functions
                                    if asyncio.iscoroutinefunction(tool_func):
                                        result = await tool_func(**args)
                                    else:
                                        result = tool_func(**args)
                                    
                                    result_text = f"\n{result}\n"
                                    callback(result_text)
                                    full_response.append(result_text)
                                    
                                except Exception as e:
                                    error_msg = f"\nError executing tool {tool_name}: {str(e)}\n"
                                    callback(error_msg)
                                    full_response.append(error_msg)
                
                    # Handle regular content
                    elif hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        callback(content)
                        full_response.append(content)
                
                # Add a small sleep to allow for cancellation checks
                await asyncio.sleep(0)
            
            return "".join(full_response)
            
        except asyncio.CancelledError:
            logger.info("OpenAI stream cancelled")
            raise CancelledError()
        except Exception as e:
            logger.error(f"Error in OpenAI stream: {e}", exc_info=True)
            raise

    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if self.current_task:
            self.cancel_current_stream()
        
        model = model or self.default_model
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        messages.extend(prompts)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_stream():
            chunks = []
            
            def collect_chunks(chunk):
                chunks.append(chunk)
                self.stream_chunk(chunk)  # Use the base class method
            
            try:
                await self.stream_message(messages, model, collect_chunks)
                return "".join(chunks)
            except CancelledError:
                return "".join(chunks) + " (cancelled)"
        
        self.current_task = asyncio.ensure_future(run_stream(), loop=loop)
        
        try:
            return loop.run_until_complete(self.current_task)
        finally:
            loop.close()