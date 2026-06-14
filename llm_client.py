# llm_client.py
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt: str, temperature: float = 0.0, max_tokens: int = 1000) -> str:
    """
    Try Groq first.
    Fall back to HuggingFace if Groq fails.
    """

    # Try Groq first
    groq_result = try_groq(prompt, temperature, max_tokens)
    if groq_result:
        return groq_result

    # Fall back to HuggingFace
    print("Groq failed — trying HuggingFace...")
    hf_result = try_huggingface(prompt, max_tokens)
    if hf_result:
        return hf_result

    # Both failed
    print("Both LLMs failed — returning None")
    return None


def try_groq(prompt: str, temperature: float, max_tokens: int) -> str:
    """Try Groq API."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON. No markdown. No explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content.strip()
        print("Groq responded")
        return result

    except Exception as e:
        print(f"Groq failed: {e}")
        return None


def try_huggingface(prompt: str, max_tokens: int) -> str:
    """Try HuggingFace Inference API as fallback."""
    try:
        import requests
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get("generated_text", "")
            print("HuggingFace responded")
            return text

        print(f"HuggingFace unexpected response: {result}")
        return None

    except Exception as e:
        print(f"HuggingFace failed: {e}")
        return None