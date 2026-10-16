from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    # base_url="http://127.0.0.1:11434/v1", hard coding it's wrong
    # api_key="fake_key",  #hard coding it's wrong
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

while True:

    user_input = input("\n YOU: ")

    if user_input.lower() in ["exit", "quit", "bye", "soja"]:
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "user", "content": user_input}],
    )

    print("Assistant messages :   ")
    print(response.choices[0].message.content)
    print(response.choices[0].message.role)

