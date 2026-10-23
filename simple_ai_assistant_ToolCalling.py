from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import json
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

messages = []

messages.append(
    {
        "role": "system",
        "content": "Act like a very humble agent and response always under 100 words ",
    }
)

while True:

    user_input = input("\n YOU: ")

    if user_input.lower() in ["exit", "quit", "bye", "soja"]:
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
            result = fn(**func_args)

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
            )

        # second call to llm api

        response = client.chat.completions.create(
            model=os.getenv("MODEL"), messages=messages
        )
        msg = response.choices[0].message

    messages.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )

    print("Assistant messages :   ")
    print(response.choices[0].message.content)
    print(response.choices[0].message.role)
