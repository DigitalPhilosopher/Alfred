import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Install packages from requirements.txt if they are missing
requirements_file = "requirements.txt"
if os.path.exists(requirements_file):
    with open(requirements_file) as f:
        required_packages = f.read().splitlines()

    for package in required_packages:
        try:
            __import__(package.split('==')[0])  # Import package (handles version specifiers)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            
import tkinter as tk
import datetime
from agent.ai import chat_with_ai

class ChatAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Assistant")
        self.root.geometry("400x500")
        self.root.attributes('-alpha', 0.9)  # Set window transparency
        
        # Container for chat messages
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.chat_frame.pack(padx=10, pady=10, expand=True, fill='both')
        
        # Scrollable frame for chat bubbles
        self.canvas = tk.Canvas(self.chat_frame, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Enable mouse scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Entry widget for user input
        self.entry_widget = tk.Entry(self.root)
        self.entry_widget.pack(padx=10, pady=10, fill='x')
        self.entry_widget.bind("<Return>", self.process_input)
        self.entry_widget.bind("<Escape>", lambda e: self.root.quit())
        
        self.log_file = "assistant.log"
        self.chat_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! Type your message and press Enter. Press Escape to exit."}
        ]
        self.add_message("Alfred", "Hello! Type your message and press Enter. Press Escape to exit.")
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def process_input(self, event):
        user_input = self.entry_widget.get().strip()
        if user_input:
            self.add_message("You", user_input, right=True)
            self.log_message(user_input)
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Call GPT-4o to get response
            assistant_response = self.chat_with_gpt_4o()
            self.add_message("Alfred", assistant_response, right=False)
            self.log_message(f"Alfred: {assistant_response}")
            self.chat_history.append({"role": "assistant", "content": assistant_response})
        self.entry_widget.delete(0, tk.END)
    
    def add_message(self, sender, message, right=False):
        bubble_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0", pady=5)
        bubble_label = tk.Label(
            bubble_frame,
            text=f"{sender}: {message}",
            padx=10,
            pady=5,
            wraplength=300,
            justify="right" if right else "left",
            bg="#add8e6" if sender == "Alfred" else "#90ee90",
            anchor="e" if right else "w"
        )
        bubble_label.pack(anchor="e" if right else "w", padx=(50 if right else 10, 10 if right else 50))
        bubble_frame.pack(anchor="e" if right else "w", fill='x', padx=10, pady=2)
        self.scrollable_frame.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")
    
    def chat_with_gpt_4o(self):
        # Function to call GPT-4o with all messages
        self.log_message("test")
        response = chat_with_ai(self.chat_history)
        return response

if __name__ == "__main__":
    root = tk.Tk()
    assistant = ChatAssistant(root)
    root.mainloop()