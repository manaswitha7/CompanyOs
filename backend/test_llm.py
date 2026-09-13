from app.services.llm.provider import LLMProvider


llm = LLMProvider()

response = llm.generate(
    "Explain what a vector database is in two sentences."
)

print("\nLLM RESPONSE")
print("=" * 70)
print(response)
