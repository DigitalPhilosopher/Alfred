# AI Strategy Implementation

This folder contains the implementation of different AI Large Language Model (LLM) strategies using a common interface. The architecture allows for easy integration of new AI providers while maintaining consistent behavior across the application.

## Base Strategy

The `AIStrategy` abstract base class (`base.py`) provides a common interface for all AI implementations. Key features include:

- Stream handling for real-time responses
- Tool/function calling support
- Consistent chat interface
- Cancellation support

### Key Methods

- `initialize_client()`: Set up the API client
- `chat(prompts, model)`: Execute chat with the AI model
- `default_model`: Property defining the default model to use
- `set_tools(tools)`: Configure available tools/functions
- `stream_chunk(chunk)`: Handle streaming responses

## Implementing a New Strategy

To add a new AI provider, create a new class that inherits from `AIStrategy`:

```python
from .base import AIStrategy
class MyNewStrategy(AIStrategy):
    def init(self, api_key: str):
        super().init()
        self.api_key = api_key
        self.client = None
    
    @property
    def default_model(self) -> str:
        return "your-default-model"
    
    def initialize_client(self) -> None:
        # Initialize your API client
        pass

    def chat(self, prompts: List[Dict[str, str]], model: Optional[str] = None) -> str:
        # Implement chat logic
        pass
```

## Implemented Strategies

### Anthropic (Claude)

The `AnthropicStrategy` implements Claude API integration with support for:
- Claude 3 Sonnet (default model)
- Streaming responses
- Tool/function calling
- Message cancellation

### OpenAI

The `OpenAIStrategy` implements OpenAI API integration with support for:
- GPT-4 Turbo (default model)
- Streaming responses
- Function calling
- Message cancellation

### Dummy Strategy

A test implementation that simulates AI responses with delays. Useful for testing and development without consuming API credits.

## Usage Example
```python
from agent.strategies import OpenAIStrategy
```

### Initialize strategy
```python
strategy = OpenAIStrategy(api_key="your-api-key")
```

### Configure tools (optional)
```python
tools = {
    "get_weather": {
        "description": "Get weather information",
        "function": get_weather_func,
        "input_schema": {
            "type": "object",
        "properties": {
            "location": {"type": "string"}
        }
    }
}
}
strategy.set_tools(tools)
```

### Set up streaming (optional)
```python
strategy.set_stream_callback(lambda chunk: print(chunk, end=""))
```

### Chat with the AI
```python
response = strategy.chat([
    {"role": "user", "content": "What's the weather like?"}
])
```

## Error Handling

All strategies include comprehensive error handling for:
- API rate limits
- Network issues
- Invalid requests
- Stream interruptions

Errors are logged using the application's logging system for debugging and monitoring.