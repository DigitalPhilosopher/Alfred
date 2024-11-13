import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()

def chat_with_gpt_4o(prompts, model="gpt-4o-mini"):
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