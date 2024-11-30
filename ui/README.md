# AI Agent UI Component

This directory contains the user interface implementation for the AI Agent chat application.

## Components

### ChatUI (chat_ui.py)
The main UI class that implements a chat interface using Tkinter. Features include:
- Semi-transparent chat window
- Message bubbles for user and AI responses
- Chat history saving
- Loading indicator
- Auto-scrolling message view
- Message logging

## Key Features
- Chat history is automatically saved in `.history` directory with date-stamped filenames
- Messages are logged to `assistant.log` with timestamps
- Escape key or window close button properly saves history before exit
- Support for asynchronous AI responses with loading indicator
- Different colored message bubbles for user (green) and AI (blue)

## Usage
The ChatUI class requires three parameters:
```python
ChatUI(root, message_callback, ai_manager)
```
- `root`: Tkinter root window
- `message_callback`: Function to handle user messages
- `ai_manager`: AI agent manager instance

## Controls
- Press Enter to send a message
- Press Escape to exit
- Mouse wheel for scrolling through chat history

	