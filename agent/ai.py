import openai
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ai_chat_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ai_chat')

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
    global client
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    logger.info(f"Attempting to initialize chat with model: {model}")
    
    # Check if Anthropic API key is available
    if anthropic_key is not None and anthropic_key.strip() != "":
        if client is None:
            logger.info("Initializing Anthropic client")
            client = Anthropic(api_key=anthropic_key)
        if model:
            return chat_with_claude(prompts, model)
        else:
            return chat_with_claude(prompts)
        
    # Check if OpenAI API key is available
    if openai_key is not None and openai_key.strip() != "":
        if client is None:
            logger.info("Initializing OpenAI client")
            client = openai.OpenAI(api_key=openai_key)
        if model:
            return chat_with_gpt(prompts, model)
        else:
            return chat_with_gpt(prompts)
        
    logger.error("No valid API keys found")
    raise ValueError("No valid API keys found for either Anthropic or OpenAI")

def chat_with_gpt(prompts, model="gpt-4o-mini"):
    try:
        logger.info(f"Starting OpenAI chat with model: {model}")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        messages += prompts
        
        logger.debug(f"Sending request to OpenAI with {len(messages)} messages")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        
        logger.info("Successfully received OpenAI response")
        return response.choices[0].message.content
        
    except openai.APIConnectionError as e:
        logger.error(f"OpenAI connection error: {e.__cause__}")
        raise
    except openai.RateLimitError as e:
        logger.error(f"OpenAI rate limit error {e.status_code}: {e.response}")
        raise
    except openai.APIStatusError as e:
        logger.error(f"OpenAI status error {e.status_code}: {e.response}")
        raise
    except openai.BadRequestError as e:
        logger.error(f"OpenAI bad request error {e.status_code}: {e.response}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI chat: {e}", exc_info=True)
        raise

def chat_with_claude(prompts, model="claude-3-5-haiku-20241022"):
    try:
        logger.info(f"Starting Anthropic chat with model: {model}")

        system = "You are a helpful assistant."
        messages=[]
        for prompt in prompts:
            if prompt["role"] == "system":
                system = prompt["content"]
            else:
                messages.append({
                    "role": prompt["role"],
                    "content": [
                        {
                            "type": "text",
                            "text": prompt["content"]
                        }
                    ]
                })

        message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0,
            system=system,
            messages=messages
        )

        logger.info("Successfully received Anthropic response")
        return message.content[0].text

    except Exception as e:
        print("error")
        # Handle specific Anthropic API errors
        if "rate_limit" in str(e).lower():
            logger.error(f"Anthropic rate limit error: {e}")
        elif "status" in str(e).lower():
            logger.error(f"Anthropic status error: {e}")
        elif "bad_request" in str(e).lower():
            logger.error(f"Anthropic bad request error: {e}")
        else:
            logger.error(f"Unexpected error in Anthropic chat: {e}", exc_info=True)
        raise