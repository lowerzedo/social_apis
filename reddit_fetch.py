import os
import praw
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

load_dotenv()

LIMIT = 2
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


@dataclass
class RedditComments:
    author: str
    score: int
    body: str


@dataclass
class SocialMediaData:
    title: Optional[str]
    url: str
    author: str
    content: str
    date: datetime
    comment: list[RedditComments]


def extract_reddit_posts(
    query: str,
    subreddit: str = "all",
    sort: str = "relevance",
    syntax: str = "lucene",
    time_filter: str = "all",
    number_of_comments: int = 5,
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

    posts = []
    for submission in reddit.subreddit(subreddit).search(
        query=query, sort=sort, syntax=syntax, time_filter=time_filter, limit=LIMIT
    ):
        # Get top-level comments
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        comments = []
        for comment in submission.comments[:number_of_comments]:
            comments.append(
                RedditComments(
                    body=comment.body, score=comment.score, author=str(comment.author)
                )
            )

        posts.append(
            SocialMediaData(
                title=submission.title,
                url=submission.url,
                author=str(submission.author),
                content=submission.selftext,
                date=datetime.fromtimestamp(submission.created_utc),
                comment=comments,
            )
        )

    return posts


reddit_posts = extract_reddit_posts(query="test")
# print(reddit_posts)

for post in reddit_posts:
    print(post.content)
    print(post.title)
    for comment in post.comment:
        print(comment.body)
