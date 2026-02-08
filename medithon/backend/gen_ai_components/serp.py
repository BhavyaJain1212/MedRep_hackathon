import os
import requests
from dotenv import load_dotenv

# Find .env in the same directory as this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def serp_search(query: str, num: int = 7, gl: str = "in", hl: str = "en"):
    """
    Search Google via SerpAPI and return structured results.
    """
    if not SERPAPI_API_KEY:
        return {"error": "SERPAPI_API_KEY not set in environment"}

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num,
        "gl": gl,
        "hl": hl,
    }

    try:
        r = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        organic = data.get("organic_results", []) or []
        results = [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "source": item.get("source")
            }
            for item in organic[:num]
        ]
        return results
    except Exception as e:
        return {"error": str(e)}
