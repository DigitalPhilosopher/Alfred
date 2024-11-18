import tkinter as tk
from management.ai_manager import AIManager
from ui import ChatUI

class ChatApplication:
    def __init__(self):
        self.ai_manager = AIManager()
        self.root = tk.Tk()
        self.assistant = ChatUI(self.root, self.ai_manager.process_message)
        
    def run(self):
        self.root.mainloop()