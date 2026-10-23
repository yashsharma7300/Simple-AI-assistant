from datetime import datetime
import requests
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
from utilities.utilities import log

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
# response = tavily_client.search("who is messi")
# print(response )


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def web_search(query: str) -> dict:
    # search web for relevant info

    try:
        response = tavily_client.search(
            query=query, max_results=5, search_depth="basic"
        )

        results = []

        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content"),
                }
            )

        return {"success": True, "query": query, "results": results}

    except Exception:
        return {"success": False, "error": "web search failed"}


def web_scrapper(url: str) -> dict:
    # "extract readablt text from a public webpage "

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "LearningAgent/1.0"},
            allow_redirects=False,
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            return
        {"success": False, "error": "URL does not retrun an html web page"}

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        title = soup.title.get_text(strip=True) if soup.title else "Untitled"

        text = soup.get_text(separator=" ", strip=True)

        return {"success": True, "url": url, "title": title, "content": text[:15000]}

    except requests.RequestException:
        return {"success": False, "error": "Unable to retrieve the webpage."}


# TOOLS = [{} , {} , {}]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current date and time as a formatted string.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "return the live current weather of a given city ",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "city to get the weather for",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "search the internet for curretn information"
                "facts , documentation and relevant web pages "
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
                "addititonalProperties": False,
            },
        },
    },
]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
    "web_search": web_search,
}


def run_tool(tool_call):
    func_name = tool_call.function.name
    func_argumnets = {}

    try:

        func_argumnets = json.loads(tool_call.function.arguments or "{}")
        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]

        log(f" {func_name}({func_argumnets})")

        result = fn(**func_argumnets)

    except Exception as e:
        result = f"Error while running {func_name}:{e} "

    log(f"   ->{result}")
    return str(result)
