import os
import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)


client=MultiServerMCPClient(
    {
        "tavily_server": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
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
        },
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

search_tool = None
aviation_tools = {}

async def initialize_mcp():
    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()
    print("\nAvailable tools: \n")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name : tool
        for tool in tools
        if tool.name == "tavily_search"
    }



async def tavily_mcp_srch(query:str):
    await initialize_mcp()

    result = await search_tool.ainvoke({
        "query" : query
    })

    return result

async def aviation_mcp_call(
        tool_name:str,
        tool_args: dict= None    
    ):
    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == "tool_name"
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result

async def get_airports():
    await initialize_mcp()

    tool = await aviation_tools.get("list_airports")

    if not tool:
        return "airport tool not available"

    result = await tool.ainvoke({})

    return result


async def get_airlines():
    await initialize_mcp()

    tool = await aviation_tools.get("list_airlines")

    if not tool:
        return "airline tool not available"

    result = await tool.ainvoke({})

    return result

restaurant_tool = None
top_restaurant_tool = None


async def initialize_restaurant_tools():

    global restaurant_tool, top_restaurant_tool

    if restaurant_tool is not None:
        return

    tools = await client.get_tools()

    restaurant_tool = next(
        t for t in tools
        if t.name == "get_near_restaurant"
    )

    top_restaurant_tool = next(
        t for t in tools
        if t.name == "get_top_restaurant"
    )


async def restaurant_mcp_search(city: str):

    await initialize_restaurant_tools()

    return await restaurant_tool.ainvoke(
        {
            "city": city
        }
    )


async def top_restaurant_mcp_search(city: str):

    await initialize_restaurant_tools()

    return await top_restaurant_tool.ainvoke(
        {
            "city": city
        }
    )

def extract_destination(query: str):

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)

    return response.content.strip()





# Here we are discovering and proving the query with the appropriate tools
async def main():
    tools = await client.get_tools()

    print("\nAvailable tools: \n")

    for tool in tools:
        print(tool.name)

    # search_tool = next(
    #     tool
    #     for tool in tools
    #     if tool.name == "tavily_search"
    # )

    # result = await search_tool.ainvoke(
    #     {
    #         "query" : "Best hotels in london"
    #     }
    # )

    # print(result)


if __name__ == "__main__":
    print("result")
    asyncio.run(main())