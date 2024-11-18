import tkinter as tk
import datetime
import threading

class ChatUI:
    def __init__(self, root, message_callback):
        self.root = root
        self.message_callback = message_callback
        self.root.title("AI Agent Alfred")
        self.root.geometry("400x500")
        self.root.attributes('-alpha', 0.9)
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.log_file = "assistant.log"
        self.loading = False
        self.add_message("Alfred", "Hello! Type your message and press Enter. Press Escape to exit.")
        
    def setup_ui(self):
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.chat_frame.pack(padx=10, pady=10, expand=True, fill='both')
        
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
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Loading indicator
        self.loading_label = tk.Label(self.root, text="Thinking...", fg="gray")
        
        self.entry_widget = tk.Entry(self.root)
        self.entry_widget.pack(padx=10, pady=10, fill='x')
        self.entry_widget.bind("<Return>", self.process_input)
        self.entry_widget.bind("<Escape>", lambda e: self.root.quit())
    
    def show_loading(self):
        self.loading = True
        self.loading_label.pack(before=self.entry_widget)
        self.entry_widget.config(state='disabled')
        
    def hide_loading(self):
        self.loading = False
        self.loading_label.pack_forget()
        self.entry_widget.config(state='normal')
    
    def process_input(self, event):
        user_input = self.entry_widget.get().strip()
        if user_input:
            self.entry_widget.delete(0, tk.END)
            self.add_message("You", user_input, right=True)
            self.log_message(user_input)
            
            self.current_message_label = None
            
            self.show_loading()
            
            def callback_wrapper():
                response = self.message_callback(user_input)
                self.root.after(0, lambda: self.handle_response(response))
            
            thread = threading.Thread(target=callback_wrapper)
            thread.start()

    def handle_response(self, response):
        self.hide_loading()
        self.log_message(f"Alfred: {response}")
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
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
        
        if sender == "Alfred":
            self.current_message_label = bubble_label
        
        bubble_frame.pack(anchor="e" if right else "w", fill='x', padx=10, pady=2)
        self.scrollable_frame.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def update_current_message(self, chunk):
        if not hasattr(self, 'current_message_label') or self.current_message_label is None:
            self.add_message("Alfred", chunk)
        else:
            current_text = self.current_message_label.cget("text")
            
            if current_text.startswith("Alfred: "):
                current_text = current_text[8:]

            if current_text:
                new_text = f"{current_text}{chunk}"
            else:
                new_text = chunk
            
            self.current_message_label.config(text=f"Alfred: {new_text}")
            
            self.scrollable_frame.update_idletasks()
            self.canvas.yview_moveto(1.0)
    
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")