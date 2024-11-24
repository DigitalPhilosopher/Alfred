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
        self.current_tool_calls = {}  # Store incomplete tool calls
    
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
            
            kwargs = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            
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
            
            stream = self.client.chat.completions.create(**kwargs)
            
            full_response = []
            for chunk in stream:
                if asyncio.current_task().cancelled():
                    raise asyncio.CancelledError()
                
                # Handle tool calls
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'tool_calls'):
                    delta = chunk.choices[0].delta
                    tool_calls = delta.tool_calls
                    
                    if tool_calls:
                        for tool_call in tool_calls:
                            tool_call_id = tool_call.id if tool_call.id else list(self.current_tool_calls.keys())[-1]
                            
                            # Initialize new tool call
                            if tool_call_id not in self.current_tool_calls:
                                self.current_tool_calls[tool_call_id] = {
                                    'function': {'name': '', 'arguments': ''},
                                    'type': 'function',
                                    'complete': False
                                }
                            
                            current_call = self.current_tool_calls[tool_call_id]
                            
                            # Update function name if present
                            if hasattr(tool_call.function, 'name') and tool_call.function.name:
                                current_call['function']['name'] = tool_call.function.name
                            
                            # Append arguments if present
                            if hasattr(tool_call.function, 'arguments') and tool_call.function.arguments:
                                current_call['function']['arguments'] += tool_call.function.arguments
                            
                            # Check if we have a complete tool call
                            try:
                                # Attempt to parse arguments as JSON to check completeness
                                if current_call['function']['name'] and current_call['function']['arguments']:
                                    json.loads(current_call['function']['arguments'])
                                    current_call['complete'] = True
                            except json.JSONDecodeError:
                                # Arguments are not complete JSON yet
                                continue
                            
                            # Execute complete tool calls
                            if current_call['complete'] and not current_call.get('executed', False):
                                try:
                                    tool_name = current_call['function']['name']
                                    logger.info(f"Executing complete tool call: {tool_name}")
                                    args = json.loads(current_call['function']['arguments'])
                                    
                                    if tool_name in self.tools:
                                        tool_func = self.tools[tool_name]["function"]
                                        
                                        if asyncio.iscoroutinefunction(tool_func):
                                            result = await tool_func(**args)
                                        else:
                                            result = tool_func(**args)
                                        
                                        result_text = f"\n{result}\n"
                                        callback(result_text)
                                        full_response.append(result_text)
                                        
                                        current_call['executed'] = True
                                    
                                except Exception as e:
                                    error_msg = f"\nError executing tool {tool_name}: {str(e)}\n"
                                    logger.error(error_msg)
                                    callback(error_msg)
                                    full_response.append(error_msg)
                                    current_call['executed'] = True
                
                    # Handle regular content
                    elif hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        callback(content)
                        full_response.append(content)
                
                await asyncio.sleep(0)
            
            # Clean up completed tool calls at the end
            self.current_tool_calls = {k: v for k, v in self.current_tool_calls.items() 
                                     if not v.get('executed', False)}
            
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
                self.stream_chunk(chunk)
            
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