import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test 1 — Groq works
print("Testing Groq...")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello in one sentence"}],
    temperature=0.0
)
print(f"Groq works: {response.choices[0].message.content}")

# Test 2 — Data loads
print("\nTesting data load...")
with open("data/england_croatia.txt", "r") as f:
    news = f.read()
print(f"Data loaded: {len(news)} characters")
print(news[:200])