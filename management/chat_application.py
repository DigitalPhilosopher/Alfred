import tkinter as tk
from management.ai_manager import AIManager
from ui import ChatUI

class ChatApplication:
    def __init__(self):
        self.ai_manager = AIManager()
        self.root = tk.Tk()
        self.assistant = ChatUI(self.root, self.ai_manager.process_message, self.ai_manager)
        self.ai_manager.set_stream_callback(self.assistant.update_current_message)
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            if hasattr(self.assistant, 'on_closing'):
                self.assistant.on_closing()