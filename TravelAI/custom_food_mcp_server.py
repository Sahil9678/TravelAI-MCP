# pip install mcp requests

from mcp.server.fastmcp import FastMCP
import requests
import os

from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Food Server")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@mcp.tool()
def get_near_restaurant(city: str):

    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={
            "query": "restaurants in {city}",
            "type": "restaurant",
            "key": GOOGLE_API_KEY,
        }
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return data

@mcp.tool()
def get_top_restaurant(city: str):

    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={
            "query": "top restaurants in {city}",
            "type": "restaurant",
            "key": GOOGLE_API_KEY,
        }
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return data


if __name__ == "__main__":
    mcp.run()