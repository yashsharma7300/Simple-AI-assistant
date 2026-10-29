# RAG STARTING

import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))



def get_embedding(text):
  response = client.embeddings.create(
       model=os.getenv("EMBED_MODEL"),
       input= text,
    )
  return response.data[0].embedding

def cosine_similarity(A,B):
  dot_prod = np.dot(A,B)
  norm_a= np.linalg.norm(A)
  norm_b= np.linalg.norm(B)
  return dot_prod / (norm_a*norm_b)

text1 = "python is a programming language"
text2 = "python is used to write AI related code snippets"
text3 = "i love eating apples every morning"

embedding1 = get_embedding(text1)
embedding2 = get_embedding(text2)
embedding3 = get_embedding(text3)

similarity12 = cosine_similarity(embedding1 , embedding2)
similarity13 = cosine_similarity(embedding1 , embedding3)
similarity23 = cosine_similarity(embedding2 , embedding3)


print("Similarity between text1 and text2: ", similarity12)
print("Similarity between text1 and text3: ", similarity13)
print("Similarity between text2 and text3: ", similarity23)
