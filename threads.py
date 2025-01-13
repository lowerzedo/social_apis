import requests
import os
from dotenv import load_dotenv

load_dotenv()


def search_threads(
    keyword, search_type="TOP", access_token=os.getenv("THREADS_APP_SECRET")
):
    url = "https://graph.threads.net/v1.0/keyword_search"
    params = {
        "q": keyword,
        "search_type": search_type,
        "fields": "id,text,media_type,permalink,timestamp,username,has_replies,is_quote_post,is_reply",
        "access_token": access_token,
    }
    response = requests.get(url, params=params)
    print(response)
    return response.json()


# Example usage
results = search_threads("dating text")
for thread in results.get("data", []):
    print(f"Username: {thread['username']}")
    print(f"Text: {thread['text']}")
    print(f"Permalink: {thread['permalink']}")
    print(f"Timestamp: {thread['timestamp']}")
    print("-" * 40)
