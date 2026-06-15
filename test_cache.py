# test_cache.py
from llm_client import call_llm
import time

prompt = 'Return this JSON: {"test": true}'

print("First call (no cache):")
start = time.time()
result1 = call_llm(prompt, temperature=0.0)
time1 = round(time.time() - start, 2)
print(f"Time: {time1}s")

if result1:
    print(f"Result: {result1[:50]}")
else:
    print("Result: None — LLM failed")

print("\nSecond call (from cache):")
start = time.time()
result2 = call_llm(prompt, temperature=0.0)
time2 = round(time.time() - start, 2)
print(f"Time: {time2}s")

if result2:
    print(f"Result: {result2[:50]}")
    if time1 > 0 and time2 > 0:
        print(f"\nSpeed improvement: {time1/time2:.0f}x faster")
else:
    print("Result: None — check API keys")