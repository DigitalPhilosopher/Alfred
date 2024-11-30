# Management Module

This module serves as the coordination layer between the UI and AI agent components of the application.

## Components

### ChatApplication (chat_application.py)
The main application class that initializes and connects the UI and AI components. It:
- Creates the Tkinter root window
- Initializes the AI management system
- Sets up the chat UI
- Configures streaming callbacks

### AIManager (ai_manager.py)
A wrapper class that manages AI agent interactions. Features include:
- Agent initialization and configuration
- Message processing
- Stream callback management
- Agent switching capability

## Architecture

```
management/
├── __init__.py
├── ai_manager.py      # AI agent management
├── chat_application.py # Main application coordinator
└── README.md         # This file
```

## Usage

```python
from management.chat_application import ChatApplication

# Initialize and run the application
app = ChatApplication()
app.run()
```

## Integration Points

### UI Layer
- Connects with `ChatUI` from the UI module
- Handles message callbacks
- Manages UI update streams

### AI Layer
- Integrates with `GeneralAgent` from the agent module
- Processes user messages
- Manages agent configuration

## Key Features
- Clean separation between UI and AI components
- Centralized message processing
- Flexible agent management
- Real-time streaming support
- Extensible architecture

## Dependencies
- `tkinter` for UI framework
- `ui` module for chat interface
- `agent` module for AI functionality
