import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


def search_restaurants(query):

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"best restaurants in {query}",
        "key": API_KEY,
    }

    response = requests.get(url, params=params)
    data = response.json()

    restaurants = []

    if data.get("status") == "OK":

        for place in data.get("results", [])[:5]:

            name = place.get("name", "Unknown")
            address = place.get("formatted_address", "No address")
            rating = place.get("rating", "N/A")
            total_ratings = place.get("user_ratings_total", 0)

            restaurants.append(
                f"**{name}** (Rating: {rating} from {total_ratings} reviews)\n   {address}"
            )
    else:
        return f"No restaurant data found. API status: {data.get('status', 'Unknown')}"

    return "\n\n".join(restaurants)