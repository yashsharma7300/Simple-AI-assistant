from openai import OpenAI
import json
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
from dotenv import load_dotenv
import os

# NO CHANGE IN THIS FILE BECAUSE WE HAVE DONE THE CHANGES IN TOOLS.PY THAT'S IT
# also , we have done changes in IF TOOLS.EXIST -> CHAIN TOOL CALLING

#  LEARNING ABOUT CHAIN TOOL CALLING  AND PARALLEL TOOL CALLING
# SEQUENTIAL CALLING


load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))


messages = []

messages.append(
    {
        "role": "system",
        "content": "provide answer in serious and efficient way under 100 words ",
    }
)


while True:

    user_ip = input("\n YOU: ")

    if user_ip.lower() in ["exit", "bye", "soja"]:
        break

    messages.append({"role": "user", "content": user_ip})

    # response = client.chat.completions.create(
    #     model=os.getenv("MODEL"),
    #     messages=messages,
    #     tools=TOOLS,
    # )

    # msg = response.choices[0].message

    # if msg.tool_calls:

    # chained tool calling
    while True:

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS,
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_argumnets = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]

            result = fn(**func_argumnets)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

        # response = client.chat.completions.create(
        #     model=os.getenv("MODEL"), messages=messages
        # )

        # msg = response.choices[0].message

    messages.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )

    print("Assistant messages :   ")
    print(response.choices[0].message.content)
    print(response.choices[0].message.role)
