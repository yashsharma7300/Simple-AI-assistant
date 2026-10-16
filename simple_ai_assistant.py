from openai import OpenAI

client = OpenAI(
    # base_url="http://127.0.0.1:11434/v1", hard coding it's wrong
    api_key="fake_key",  #hard coding it's wrong 
)

response = client.chat.completions.create(
    model="qwen3:4b", messages=[{"role": "user", "content": "Hello LLM Bro"}]
)

print("response : ")
print(response)

print("-----------------------------------")
print("chat messages :   ")
print(response.choices[0].message)

#  olllama -> json -> python object (chat completion )
