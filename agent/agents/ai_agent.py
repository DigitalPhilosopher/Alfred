from typing import Optional, List, Dict, Callable
from dotenv import load_dotenv
import os
from ..strategies import OpenAIStrategy, AnthropicStrategy, AIStrategy, DummyStrategy
from ..logger_config import logger

class AIAgent:
    def __init__(self):
        self.strategy: Optional[AIStrategy] = None
        self.on_stream: Optional[Callable[[str], None]] = None
        self.init_chat_history()
    
    def init_chat_history(self):
        self.chat_history = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "assistant", "content": "Hello! Type your message and press Enter. Press Escape to exit."}
        ]

    def system_prompt(self) -> str:
        return """# ALFRED is an AI agent designed to assist with research, engineering, and development projects. It has the following core capabilities:

## Projects:
- Can initiate a new programming project with the command "Open project: [project name]". This creates a dedicated project agent to assist with that specific software development effort.
- Only one project can be active at a time. Starting a new project will close the previous one.
- The project agent has knowledge of software engineering principles, programming languages, development tools, and best practices. It can help with design, implementation, testing, and debugging.
- The agent maintains the current project state and context. It can answer questions, provide guidance, and assist with coding tasks relevant to the active project.

## Research:
- Can initiate new research efforts with the command "Begin research on: [research topic]". This spins up a new research agent dedicated to that topic.
- The research agent can conduct literature reviews, summarize key findings, identify open questions, brainstorm hypotheses and experiments, analyze data, and assist with writing research papers on the specified topic.

## Applications:
- Can open applications on the user's computer with commands like "Open application: [app name]". Currently supported apps: Visual Studio Code, Jupyter Notebook, Terminal.
- Provides a natural language interface for interacting with and controlling the opened applications to facilitate software development.

## General Assistance:
- When not given a specific command, ALFRED can engage in open-ended conversation and provide knowledgeable answers on a wide range of topics.
- Maintains context of the current conversation and task to provide relevant and helpful information.
- Has broad knowledge spanning computer science, software engineering, math, science, and technology that it can draw upon.

ALFRED aims to be a capable and personable assistant to enhance your productivity in software development and research pursuits. Let me know how I can help!"""
        
    def initialize_strategy(self) -> None:
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        debug = os.getenv('DEBUG')
        
        if debug == "True":
            self.strategy = DummyStrategy("")
        elif anthropic_key and anthropic_key.strip():
            self.strategy = AnthropicStrategy(anthropic_key)
        elif openai_key and openai_key.strip():
            self.strategy = OpenAIStrategy(openai_key)
        else:
            logger.error("No valid API keys found")
            raise ValueError("No valid API keys found for either Anthropic or OpenAI")
        
        if hasattr(self.strategy, 'on_stream'):
            self.strategy.on_stream = self.on_stream
    
    def set_stream_callback(self, callback: Callable[[str], None]):
        self.on_stream = callback
        if self.strategy and hasattr(self.strategy, 'on_stream'):
            self.strategy.on_stream = callback

    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the chat history."""
        self.chat_history.append({"role": role, "content": content})

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history

    def chat(self, message: str, model: Optional[str] = None) -> str:
        """Process a single message and return the response."""
        if not self.strategy:
            self.initialize_strategy()
        
        self.add_message("user", message)
        response = self.strategy.chat(self.chat_history, model)
        self.add_message("assistant", response)
        return response