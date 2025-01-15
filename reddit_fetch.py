import os
import praw
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

load_dotenv()

LIMIT = 2
NUMBER_OF_COMMENTS = 2
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


@dataclass
class SocialMediaData:
    # id: str  # Unique identifier
    type: str  # "post" or "comment"
    title: Optional[str]  # Will be None for comments
    url: str
    author: str
    content: str  # selftext for posts, body for comments
    date: datetime
    parent_id: Optional[str]  # Will be None for posts, post_id for comments


def extract_reddit_posts(
    query: str,
    subreddit: str = "all",
    sort: str = "relevance",
    syntax: str = "lucene",
    time_filter: str = "all",
    number_of_comments: int = NUMBER_OF_COMMENTS,
) -> list[SocialMediaData]:
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
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    items = []
    for submission in reddit.subreddit(subreddit).search(
        query=query, sort=sort, syntax=syntax, time_filter=time_filter, limit=LIMIT
    ):
        # Add the post
        items.append(
            SocialMediaData(
                # id=submission.id,
                type="post",
                title=submission.title,
                url=submission.url,
                author=str(submission.author),
                content=submission.selftext,
                date=datetime.fromtimestamp(submission.created_utc),
                parent_id=None,
            )
        )

        # Add the comments
        submission.comments.replace_more(limit=0)
        for comment in submission.comments[:number_of_comments]:
            items.append(
                SocialMediaData(
                    # id=comment.id,
                    type="comment",
                    title=None,
                    url=f"https://reddit.com{comment.permalink}",
                    author=str(comment.author),
                    content=comment.body,
                    date=datetime.fromtimestamp(comment.created_utc),
                    parent_id=submission.id,
                )
            )

    return items


reddit_posts = extract_reddit_posts(query="Software Engineers")
# print(reddit_posts)

for post in reddit_posts:
    print(post.content)
    print(post.title)
    print(post.type)
    print(post.url)
    print(post.author)
    print(post.parent_id)
