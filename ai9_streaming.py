import json
import os


from openai import OpenAI
from dotenv import load_dotenv


from tools import TOOLS, run_tool
from utilities.utilities import log



load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))


messages = []
MAX_STEPS = 5  # SAFTEY LIMIT


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
    for step in range(MAX_STEPS):

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS,
            stream=True
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        log(f"Step {step+1} : model requested {len(msg.tool_calls)} ")

        messages.append(msg)

        for tool_call in msg.tool_calls:
            result = run_tool(tool_call)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

        else:
            # we ran out of steps , the model never gave final answer
            fallback = "sorry , i coud not finish this within step limits"
            messages.append({"role": "assistant", "content": fallback})
            print("assistant : " + fallback)
            continue

        # response = client.chat.completions.create(
        #     model=os.getenv("MODEL"), messages=messages
        # )

        # msg = response.choices[0].message

    messages.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )

    print("Assistant messages :   " + (msg.content or ""))
    print(response.choices[0].message.content)
    print(response.choices[0].message.role)
