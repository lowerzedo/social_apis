import praw
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_reddit_posts(
    query,
    subreddit="all",
    sort="relevance",
    syntax="lucene",
    time_filter="all",
    limit=10,
):
    """
    Fetch posts from Reddit based on the given query and parameters.

    :param query: The query string to search for.
    :param subreddit: Subreddit to search in (default: "all").
    :param sort: Sorting method, e.g., "relevance", "hot", "top", "new", or "comments" (default: "relevance").
    :param syntax: Query syntax, e.g., "cloudsearch", "lucene", or "plain" (default: "lucene").
    :param time_filter: Time filter, e.g., "all", "day", "hour", "month", "week", or "year" (default: "all").
    :param limit: Maximum number of posts to fetch (default: 10).
    :return: A list of posts with their titles and URLs.
    """
    # Initialize Reddit API client
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    # Fetch posts
    posts = []
    for submission in reddit.subreddit(subreddit).search(
        query=query, sort=sort, syntax=syntax, time_filter=time_filter, limit=limit
    ):
        # Get top-level comments
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        comments = []
        for comment in submission.comments[:5]:  # Get first 5 comments
            comments.append(
                {
                    "body": comment.body,
                    "score": comment.score,
                    "author": str(comment.author),
                }
            )

        posts.append(
            {
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "subreddit": submission.subreddit.display_name,
                "comments": comments,
            }
        )

    return posts


# Example usage
if __name__ == "__main__":
    query = "online dating problems"
    subreddit = "dating"
    sort = "top"
    time_filter = "week"
    limit = 200

    posts = fetch_reddit_posts(
        query, subreddit=subreddit, sort=sort, time_filter=time_filter, limit=limit
    )
    for post in posts:
        print(
            f"Title: {post['title']}\nURL: {post['url']}\nScore: {post['score']}\nSubreddit: {post['subreddit']}\n"
        )
        print("Top Comments:")
        for i, comment in enumerate(post["comments"], 1):
            print(f"{i}. By {comment['author']} (Score: {comment['score']}):")
            print(f"   {comment['body']}\n")
        print("-" * 80 + "\n")
