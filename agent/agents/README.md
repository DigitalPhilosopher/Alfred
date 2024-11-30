# AI Agents Implementation

This folder contains the implementation of different AI agents that use the strategy pattern for LLM interactions. The architecture provides a flexible hierarchy of agents with different responsibilities while maintaining consistent behavior.

## Agent Architecture

### Base Agent (AIAgent)

The `AIAgent` abstract base class (`ai_agent.py`) provides the foundation for all agent implementations with features including:

- Strategy pattern integration for AI providers (OpenAI, Anthropic)
- Chat history management
- Tool/function registration and handling
- Environment configuration
- Stream callback support

### Specialized Agents

#### GeneralAgent
The top-level agent that handles:
- Project management and navigation
- Application launching
- High-level research and development tasks
- Creation of specialized agents

#### ProjectAgent
A context-aware agent that:
- Maintains project-specific context
- Assists with development tasks
- Provides project-relevant guidance
- Understands project environment

## Usage Example

```python
from agent.agents import GeneralAgent

# Initialize a general agent
agent = GeneralAgent()

# Register environment variables
agent.environment_setup({
    "project_path": "/path/to/projects"
})

# Set up streaming (optional)
agent.set_stream_callback(lambda chunk: print(chunk, end=""))

# Chat with the agent
response = agent.chat("Can you help me start a new Python project?")
```

## Tool Registration

Agents can register tools that extend their capabilities:

```python
agent.register_tool(
    name="list_projects",
    func=list_projects_function,
    description="Lists all available projects",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
```

## Strategy Integration

Agents automatically select and initialize the appropriate AI strategy based on available API keys:
- Anthropic (Claude) - Primary
- OpenAI (GPT) - Fallback
- Dummy - Debug mode

See the [strategies README](../strategies/README.md) for more details on the AI implementations.

## Error Handling

The agent system includes error handling for:
- Missing API credentials
- Strategy initialization failures
- Tool execution errors
- Invalid environment configurations

Errors are logged using the application's logging system for debugging and monitoring.
