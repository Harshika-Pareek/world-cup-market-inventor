# test_client.py
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Check keys are loaded
print(f"GROQ_API_KEY exists: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"HF_TOKEN exists: {bool(os.getenv('HF_TOKEN'))}")

# Now test LLM
from llm_client import call_llm

print("\nCalling LLM...")
result = call_llm(
    "Say hello in one sentence",
    temperature=0.0
)
print(f"Result: {result}")