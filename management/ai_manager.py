from agent import AIAgent

class AIManager:
    def __init__(self):
        self.agent = AIAgent()
        self.chat_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! Type your message and press Enter. Press Escape to exit."}
        ]
        
    def process_message(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.agent.chat(self.chat_history)
        self.chat_history.append({"role": "assistant", "content": response})
        return response