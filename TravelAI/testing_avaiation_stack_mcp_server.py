import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

client=MultiServerMCPClient(
    {
        "aviationstack": {
            "transport": "stdio",
            "command": r"C:\Users\B01005183\Desktop\TravelAI-MCP-main\TravelAI\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY
            }
        }
    }
)

async def main():
    tools = await client.get_tools()

    print("\nAvailable tools: \n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())