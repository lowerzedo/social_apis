import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Twitter API credentials
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
if not BEARER_TOKEN or BEARER_TOKEN == "None":
    raise ValueError("BEARER_TOKEN not found in environment variables")


def create_headers():
    """Create headers for API request"""
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}


def fetch_tweets(keyword, max_results=10, start_days_ago=7):
    """
    Fetch tweets based on a keyword using Twitter API v2.

    Parameters:
        keyword (str): The keyword to search for.
        max_results (int): Number of tweets to fetch per request (max 100 for basic track).
        start_days_ago (int): How many days ago to start the search.

    Returns:
        list: A list of tweets matching the query.
    """
    try:
        # Define the search parameters
        start_time = (datetime.utcnow() - timedelta(days=start_days_ago)).isoformat(
            "T"
        ) + "Z"

        # API v2 endpoint
        url = "https://api.twitter.com/2/tweets/search/recent"

        # Query parameters
        params = {
            "query": f"{keyword} lang:en",
            "max_results": min(max_results, 100),  # API v2 has a max of 100 per request
            "start_time": start_time,
            "tweet.fields": "id,text,author_id,created_at",
        }

        # Make the request
        response = requests.get(url, headers=create_headers(), params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return []

        # Parse response
        json_response = response.json()
        tweets = []

        if "data" in json_response:
            for tweet in json_response["data"]:
                tweets.append(
                    {
                        "id": tweet["id"],
                        "text": tweet["text"],
                        "author_id": tweet["author_id"],
                        "created_at": tweet["created_at"],
                    }
                )
        return tweets

    except Exception as e:
        print(f"Error: {e}")
        return []


# Example usage
if __name__ == "__main__":
    keyword = "dating text"
    tweets = fetch_tweets(keyword, max_results=10, start_days_ago=1)

    if tweets:
        print(f"Found {len(tweets)} tweets:")
        for tweet in tweets:
            print(f"{tweet['created_at']} - {tweet['text']}")
    else:
        print("No tweets found.")
