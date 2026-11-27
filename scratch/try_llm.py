import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("PRIMARY_BASE_URL"),
    api_key=os.getenv("PRIMARY_API_KEY")
)
response = client.chat.completions.create(
    model=os.getenv("PRIMARY_MODEL"),
    messages=[
        {"role": "system", "content": "You are Solana, a concise personal assistant."},
        {"role": "user", "content": "Say hello and introduce yourself, and tell me what you can do in one sentence."},
    ]
)

print(response.choices[0].message.content)