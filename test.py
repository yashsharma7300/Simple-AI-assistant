from datetime import datetime
import requests
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
response = tavily_client.search("who is messi")
print(response.items)

