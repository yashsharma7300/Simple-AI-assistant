import json
import os
from types import SimpleNamespace


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


def stream_chat(history):
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True,
    )

    full_response = ""
    calls = {}

    label_printed = False

    #  streaming started
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # do we have message from the LLM

            # 1. content streaming

            if delta.content:
                if not label_printed:
                    print("🎰 Assistant :  ", end="", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True)
                full_response += delta.content

            # 2. tool calls

            for tc in delta.tool_calls or []:
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(
                        id=None, function=SimpleNamespace(name="", arguments="")
                    ),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
        print("\n stopped by user")
        calls = {}

    if label_printed:
        print()  # move to next line after assistant msg

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])

    return full_response, calls_list


def build_tool_calls_payload(tool_calls):
    # "convert collected tool calls into dict format that api expects inside an assistant messages "

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }
        payload.append(tool_call_dict)

    return payload


# chat loop
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

        full_response, tool_calls = stream_chat(messages)

        # msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"Step {step+1} : model requested {len(tool_calls)} ")

        messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "tool_calls": build_tool_calls_payload(tool_calls),
            }
        )

        for tool_call in tool_calls:
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

    # messages.append(
    #     {"role": "assistant", "content": response.choices[0].message.content}
    # )

    # print("Assistant messages :   " + (msg.content or ""))
    # print(response.choices[0].message.content)
    # print(response.choices[0].message.role)
