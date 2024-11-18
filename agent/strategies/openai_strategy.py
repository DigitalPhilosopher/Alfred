import openai
from typing import List, Dict, Optional
from .base import AIStrategy
from ..logger_config import logger
from concurrent.futures import CancelledError
import asyncio

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
            
            # Create the stream without await
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            full_response = []
            # Process the synchronous stream in chunks
            for chunk in stream:
                if asyncio.current_task().cancelled():
                    raise asyncio.CancelledError()
                    
                if chunk.choices[0].delta.content:
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