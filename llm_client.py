# llm_client.py — updated with cache

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_DISABLED = False


def call_llm(
    prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 1000,
    use_cache: bool = True
) -> str:
    """
    LLM Router with caching:
    Cache → Groq → Gemini → Ollama → None

    Caching rules:
    temperature 0.0: CACHE (deterministic outputs)
    temperature 0.8: NO CACHE (want variety)

    Why:
    Extractor (temp 0.0) = same input same output = cache
    Critic (temp 0.0) = same market same scores = cache
    Generator (temp 0.8) = want different markets = no cache
    """
    global GROQ_DISABLED

    # Only cache deterministic calls
    should_cache = use_cache and temperature == 0.0

    # Check cache first
    if should_cache:
        from utils.cache import get_cached, save_cache
        cached = get_cached(prompt)
        if cached:
            return cached

    # Try Groq
    if not GROQ_DISABLED:
        result = try_groq(prompt, temperature, max_tokens)
        if result:
            if should_cache:
                save_cache(prompt, result)
            return result
        GROQ_DISABLED = True
        print("[LLM ROUTER] Groq disabled → trying Gemini")

    # Try Gemini
    result = try_gemini(prompt, max_tokens)
    if result:
        if should_cache:
            save_cache(prompt, result)
        return result

    # Try Ollama
    result = try_ollama(prompt, max_tokens)
    if result:
        if should_cache:
            save_cache(prompt, result)
        return result

    print("[LLM ROUTER] ALL LLMs FAILED")
    return None


def try_groq(prompt: str, temperature: float,
             max_tokens: int) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]

        for model in models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                text = response.choices[0].message.content.strip()
                print(f"[Groq] OK — {model}")
                return text

            except Exception as model_err:
                err = str(model_err).lower()
                if "rate limit" in err or "tokens" in err:
                    print(f"[Groq] {model} rate limited → next")
                    continue
                print(f"[Groq] {model} error: {model_err}")
                continue

        return None

    except Exception as e:
        print(f"[Groq] Client error: {e}")
        return None


def try_gemini(prompt: str, max_tokens: int) -> str:
    try:
        import google.generativeai as genai
        genai.configure(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        if not text:
            return None
        print("[Gemini] OK")
        return text
    except Exception as e:
        print(f"[Gemini] Failed: {e}")
        return None


def try_ollama(prompt: str, max_tokens: int) -> str:
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        text = response.json().get("response", "")
        if not text or len(text.strip()) < 10:
            return None
        print("[Ollama] OK")
        return text.strip()
    except Exception as e:
        print(f"[Ollama] Failed: {e}")
        return None