from typing import List, Dict, Optional
from .base import AIStrategy
from time import sleep
import asyncio
from concurrent.futures import CancelledError

class DummyStrategy(AIStrategy):
    def __init__(self, api_key: str):
        super().__init__()  # Call parent class init
        self.current_task = None
    
    def initialize_client(self) -> None:
        pass
    
    @property
    def default_model(self) -> str:
        pass
    
    def cancel_current_stream(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
    
    async def stream_message(self, callback):
        try:
            callback("Streaming")
            await asyncio.sleep(2)
            callback(" dummy")
            await asyncio.sleep(2)
            callback(" message")
            return "Streaming dummy message"
        except asyncio.CancelledError:
            raise CancelledError()

    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if self.current_task:
            self.cancel_current_stream()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_stream():
            chunks = []
            
            def collect_chunks(chunk):
                chunks.append(chunk)
                self.stream_chunk(chunk)  # Use the base class method
            
            try:
                await self.stream_message(collect_chunks)
                return "".join(chunks)
            except CancelledError:
                return "".join(chunks) + " (cancelled)"
        
        self.current_task = asyncio.ensure_future(run_stream(), loop=loop)
        
        try:
            return loop.run_until_complete(self.current_task)
        finally:
            loop.close()