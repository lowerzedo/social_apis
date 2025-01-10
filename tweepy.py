import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Twitter API credentials
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
if not BEARER_TOKEN or BEARER_TOKEN == "None":
    raise ValueError("BEARER_TOKEN not found in environment variables")

print("BEARER_TOKEN")
print(BEARER_TOKEN)

# Initialize the Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)


def fetch_tweets(keyword, max_results=10, start_days_ago=7):
    """
    Fetch tweets based on a keyword using Twitter's Academic Research track.

    Parameters:
        keyword (str): The keyword to search for.
        max_results (int): Number of tweets to fetch per request (max 500).
        start_days_ago (int): How many days ago to start the search.

    Returns:
        list: A list of tweets matching the query.
    """
    try:
        # Define the search parameters
        start_time = (datetime.utcnow() - timedelta(days=start_days_ago)).isoformat(
            "T"
        ) + "Z"
        query = f"{keyword} lang:en"  # Add filters, e.g., language

        # Fetch tweets
        response = client.search_recent_tweets(
            query=query,
            start_time=start_time,
            max_results=max_results,
            tweet_fields=["id", "text", "author_id", "created_at"],
        )

        # Parse response
        tweets = []
        if response.data:
            for tweet in response.data:
                tweets.append(
                    {
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "created_at": tweet.created_at,
                    }
                )
        return tweets

    except tweepy.TooManyRequests:
        print("Rate limit exceeded. Please wait and try again.")
        return []
    except tweepy.TweepyException as e:
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
