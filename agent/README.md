# AI Agent System

A flexible and extensible AI agent system that implements the strategy pattern for LLM interactions. This system provides a hierarchical structure of agents with different responsibilities while maintaining consistent behavior across different AI providers.

## Architecture Overview

```
agent/
├── agents/            # Agent implementations
├── strategies/        # AI provider strategies
├── functions/        # Tool functions for agents
└── README.md         # This file
```

## Key Components

### Agents
The system implements a hierarchy of specialized agents:
- **Base Agent (AIAgent)**: Foundation class with core functionality
- **GeneralAgent**: Top-level agent for project management and task delegation
- **ProjectAgent**: Context-aware agent for project-specific tasks

[See agents documentation](agents/README.md)

### Strategies
Implements different LLM providers using a common interface:
- Anthropic (Claude) - Primary strategy
- OpenAI (GPT) - Fallback strategy
- Dummy - Debug implementation

[See strategies documentation](strategies/README.md)

### Functions
Modular tool functions that extend agent capabilities:
- Project management tools
- Development assistance functions
- Environment utilities

[See functions documentation](functions/README.md)

## Quick Start

```python
from agent.agents import GeneralAgent

# Initialize agent
agent = GeneralAgent()

# Configure environment
agent.environment_setup({
    "project_path": "/path/to/projects"
})

# Enable streaming (optional)
agent.set_stream_callback(lambda chunk: print(chunk, end=""))

# Interact with agent
response = agent.chat("Help me start a new Python project")
```

## Features

- Strategy pattern for flexible AI provider integration
- Hierarchical agent system with specialized responsibilities
- Extensible tool/function registration
- Stream support for real-time responses
- Comprehensive error handling
- Environment configuration management

## Error Handling

The system includes robust error handling for:
- Missing API credentials
- Strategy initialization failures
- Tool execution errors
- Invalid configurations

Errors are logged through the application's logging system for debugging and monitoring.

## Contributing

When adding new components:
1. Follow the existing directory structure
2. Include comprehensive documentation
3. Implement proper error handling
4. Add usage examples
5. Update relevant README files

## License

[Add your license information here]
