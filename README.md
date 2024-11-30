# AI Assistant Application

A flexible AI chat application that integrates multiple language models with a user-friendly interface.

## Overview

This application provides a desktop chat interface for interacting with AI language models, featuring:
- Support for multiple AI providers (Anthropic Claude, OpenAI GPT)
- User-friendly Tkinter-based interface
- Automatic chat history saving
- Real-time streaming responses
- Extensible agent system

## Installation

1. Clone the repository:

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment variables:
Create a `.env` file with your API keys:
```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## Usage

Run the application:
```bash
python assistant.pyw
```

### Controls
- Press Enter to send a message
- Press Escape to exit
- Use mouse wheel to scroll through chat history

## Project Structure

```
├── agent/              # AI agent implementation
│   ├── agents/        # Agent classes
│   ├── strategies/    # AI provider strategies
│   └── functions/     # Tool functions
├── management/         # Application coordination
│   ├── ai_manager.py
│   └── chat_application.py
├── ui/                 # User interface components
├── assistant.pyw       # Main application entry
└── requirements.txt    # Project dependencies
```

## Features

### UI Components
- Semi-transparent chat window
- Message bubbles for user and AI responses
- Auto-scrolling message view
- Loading indicator
- Automatic chat history saving

### AI System
- Multiple AI provider support
- Hierarchical agent system
- Real-time response streaming
- Extensible tool functions
- Comprehensive error handling

### Management Layer
- Seamless UI and AI integration
- Centralized message processing
- Flexible agent configuration

## Dependencies

- openai - OpenAI API integration
- anthropic - Anthropic Claude API integration
- python-dotenv - Environment configuration
- tk - GUI framework

## Contributing

[Add your contribution guidelines here]

## License

[Add your license information here]
