import os
from dotenv import load_dotenv
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
#load_dotenv()
load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = MultiServerMCPClient(
    {
        "restaurant": {
            "transport": "stdio",
            "command": r"C:\Users\B01005183\Desktop\TravelAI-MCP-main\langgraph_env3\Scripts\python.exe",
            "args": [
                r"C:\Users\B01005183\Desktop\TravelAI-MCP-main\TravelAI\custom_food_mcp_server.py"
            ],
            "env": {
                "GOOGLE_API_KEY": GOOGLE_API_KEY
            }
        }
    }
)

async def main():

    print("Loading tools...")

    tools = await client.get_tools()

    print("Tools loaded!")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())