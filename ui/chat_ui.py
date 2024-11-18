import tkinter as tk
import datetime
import threading
from tkinter import font as tkfont
import re

def has_markdown(text):
    """Check if text contains markdown formatting."""
    markdown_patterns = [
        r'\*\*.+?\*\*',  # Bold
        r'\*.+?\*',      # Italic
        r'`.+?`',        # Inline code
        r'^# .+$',       # Headers
        r'^- .+$',       # Unordered lists
        r'^\d+\. .+$',   # Ordered lists
    ]
    
    return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)

class MarkdownParser:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
        # Create font configurations
        default_font = tkfont.nametofont(text_widget.cget("font"))
        self.normal_font = default_font.actual()
        
        self.bold_font = default_font.copy()
        self.bold_font.configure(weight="bold")
        
        self.italic_font = default_font.copy()
        self.italic_font.configure(slant="italic")
        
        self.code_font = tkfont.Font(family="Courier", size=default_font.actual()["size"])
        
        # Configure tags
        text_widget.tag_configure("bold", font=self.bold_font)
        text_widget.tag_configure("italic", font=self.italic_font)
        text_widget.tag_configure("code", font=self.code_font, background="#f0f0f0")
        text_widget.tag_configure("heading", font=(default_font.actual()["family"], 12, "bold"))
    
    def parse_and_insert(self, text):
        # Clear existing content
        self.text_widget.delete("1.0", tk.END)
        
        lines = text.split('\n')
        for line in lines:
            # Handle headers
            if line.startswith('# '):
                self.text_widget.insert(tk.END, line[2:] + '\n', "heading")
                continue
            
            pos = "1.0"
            # Handle inline formatting
            while line:
                # Bold
                bold_match = re.match(r'\*\*(.+?)\*\*', line)
                # Italic
                italic_match = re.match(r'\*(.+?)\*', line)
                # Inline code
                code_match = re.match(r'`(.+?)`', line)
                
                if bold_match:
                    self.text_widget.insert(tk.END, bold_match.group(1), "bold")
                    line = line[len(bold_match.group(0)):]
                elif italic_match:
                    self.text_widget.insert(tk.END, italic_match.group(1), "italic")
                    line = line[len(italic_match.group(0)):]
                elif code_match:
                    self.text_widget.insert(tk.END, code_match.group(1), "code")
                    line = line[len(code_match.group(0)):]
                else:
                    next_special = re.search(r'\*\*|\*|`', line)
                    if next_special:
                        self.text_widget.insert(tk.END, line[:next_special.start()])
                        line = line[next_special.start():]
                    else:
                        self.text_widget.insert(tk.END, line)
                        break
            
            self.text_widget.insert(tk.END, '\n')

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
            
            # Reset current message label before starting new response
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
        
        # Only use markdown parsing for Alfred's messages
        if sender == "Alfred" and has_markdown(message):
            # Use Text widget for markdown support
            text_widget = tk.Text(
                bubble_frame,
                width=40,
                height=4,
                wrap=tk.WORD,
                padx=10,
                pady=5,
                bg="#add8e6",
                relief=tk.FLAT,
                highlightthickness=0
            )
            
            # Initialize markdown parser
            markdown_parser = MarkdownParser(text_widget)
            markdown_parser.parse_and_insert(f"{sender}: {message}")
            
            # Configure text widget
            text_widget.configure(state='disabled')  # Make read-only
            text_widget.pack(anchor="w", padx=(10, 50))
            
            # Adjust height based on content
            text_widget.height = int(text_widget.get("1.0", tk.END).count('\n')) + 1
            
            if sender == "Alfred":
                self.current_message_label = text_widget
        else:
            # Use regular Label for non-markdown messages
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
            # Get current text regardless of widget type
            if isinstance(self.current_message_label, tk.Text):
                current_text = self.current_message_label.get("1.0", tk.END).strip()
            else:
                current_text = self.current_message_label.cget("text")
                
            # Remove prefix if present
            if current_text.startswith("Alfred: "):
                current_text = current_text[7:]
            
            # Combine current text with new chunk
            new_text = f"{current_text}{chunk}"
            
            # Check if complete message contains markdown
            if has_markdown(new_text):
                # If current widget is a Label, switch to Text widget
                if not isinstance(self.current_message_label, tk.Text):
                    self.current_message_label.destroy()
                    self.add_message("Alfred", new_text)
                else:
                    # Update existing Text widget
                    self.current_message_label.configure(state='normal')
                    self.current_message_label.delete("1.0", tk.END)
                    markdown_parser = MarkdownParser(self.current_message_label)
                    markdown_parser.parse_and_insert(f"Alfred: {new_text}")
                    self.current_message_label.configure(state='disabled')
            else:
                # If no markdown, use simple Label
                if isinstance(self.current_message_label, tk.Text):
                    # Switch from Text to Label
                    self.current_message_label.destroy()
                    bubble_frame = self.current_message_label.master
                    self.current_message_label = tk.Label(
                        bubble_frame,
                        text=f"Alfred: {new_text}",
                        padx=10,
                        pady=5,
                        wraplength=300,
                        justify="left",
                        bg="#add8e6",
                        anchor="w"
                    )
                    self.current_message_label.pack(anchor="w", padx=(10, 50))
                else:
                    # Update existing Label
                    self.current_message_label.config(text=f"Alfred: {new_text}")
            
            self.scrollable_frame.update_idletasks()
            self.canvas.yview_moveto(1.0)
    
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")