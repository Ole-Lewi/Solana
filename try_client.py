from solana_ai.config import load_providers
from solana_ai.llm import LLMClient

client = LLMClient(load_providers())

history = [
    {"role": "system", "content": "You are Solana, a concise personal assistant."},
    {"role": "user", "content": "My Favourite colour is blue. Remember this for future reference."},
]
reply = client.chat(history)
print(reply["content"])

history.append(reply)
history.append({"role": "user", "content": "what is my favourite colour?"})
print(client.chat(history)["content"])