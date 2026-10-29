# RAG STARTING

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

# print(client)
# print()
# print("----------------------")

response = client.embeddings.create(
    model=os.getenv("EMBED_MODEL"),
    input=["I am a good boy", "python is here", "he is a good coder"],
)

# print(response)
# print()
# print("---------------------------------------")


for i, emb in enumerate(response.data):
    print(f"Embedding {i} length: {len(emb.embedding)}")
    print(emb.embedding[:5])
