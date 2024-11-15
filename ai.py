import openai
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = None

def chat_with_ai(prompts, model=None):
    """
    Routes chat requests to either Claude or ChatGPT based on available API keys.
    Prioritizes using whichever API key is provided.
    
    Args:
        prompts (list): List of message dictionaries with 'role' and 'content' keys
        model (str, optional): Specific model to use. If None, uses default models.
    
    Returns:
        str: Response text from the AI model
    
    Raises:
        ValueError: If no API keys are configured
        Exception: For various API-specific errors
    """
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    # Check if Anthropic API key is available
    if anthropic_key is not None and anthropic_key.strip() != "":
        if client is None:
            client = Anthropic(api_key=anthropic_key)
        return chat_with_claude(prompts, model)
        
    # Check if OpenAI API key is available
    if openai_key is not None and openai_key.strip() != "":
        if client is None:
            client = openai.OpenAI(api_key=openai_key)
        return chat_with_gpt(prompts, model)
        
    raise ValueError("No valid API keys found for either Anthropic or OpenAI")



def chat_with_gpt(prompts, model="gpt-4o-mini"):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        messages += prompts
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print("Server connection error: {e.__cause__}")  # from httpx.
        raise
    except openai.RateLimitError as e:
        print(f"OpenAI RATE LIMIT error {e.status_code}: (e.response)")
        raise
    except openai.APIStatusError as e:
        print(f"OpenAI STATUS error {e.status_code}: (e.response)")
        raise
    except openai.BadRequestError as e:
        print(f"OpenAI BAD REQUEST error {e.status_code}: (e.response)")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

def chat_with_claude(prompts, model="claude-3-5-haiku-202410122"):
    try:
        # Convert OpenAI-style messages to Anthropic format
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        for prompt in prompts:
            role = prompt["role"]
            content = prompt["content"]
            
            # Map OpenAI roles to Anthropic roles
            if role == "user":
                messages.append({"role": "user", "content": content})
            elif role == "assistant":
                messages.append({"role": "assistant", "content": content})
            # System messages are handled differently in Anthropic's API
            # We'll add system message content to the first user message
            elif role == "system" and messages:
                if messages[0]["role"] == "user":
                    messages[0]["content"] = f"{content}\n\n{messages[0]['content']}"
            elif role == "system":
                messages.append({"role": "user", "content": content})

        # Create the message
        response = client.messages.create(
            model=model,
            messages=messages,
            max_tokens=1024
        )

        return response.content[0].text

    except Exception as e:
        # Handle specific Anthropic API errors
        if "rate_limit" in str(e).lower():
            print(f"Anthropic API rate limit error: {e}")
        elif "status" in str(e).lower():
            print(f"Anthropic API status error: {e}")
        elif "bad_request" in str(e).lower():
            print(f"Anthropic API bad request error: {e}")
        else:
            print(f"An unexpected error occurred: {e}")
        raise