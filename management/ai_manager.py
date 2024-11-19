from agent import AIAgent

class AIManager:
    def __init__(self):
        self.agent = AIAgent()
        
    def set_stream_callback(self, callback):
        self.agent.set_stream_callback(callback)
        
    def process_message(self, user_input):
        return self.agent.chat(user_input)