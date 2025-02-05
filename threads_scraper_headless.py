from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Dict
import json
from parsel import Selector
from nested_lookup import nested_lookup
import jmespath

from playwright.sync_api import sync_playwright


@dataclass
class ThreadsPost:
    post_id: str
    pk: str
    code: str
    url: str
    user_name: str
    content: str
    published_on: int
    posted_at: datetime
    reply_count: int
    like_count: int
    user_pic: str
    user_verified: bool
    images: list
    image_count: int
    videos: list
    has_audio: bool
    user_pk: str
    user_id: str


def parse_thread(data: Dict) -> ThreadsPost:
    """Parse a Threads post JSON dataset into a ThreadsPost dataclass."""
    result = jmespath.search(
        """{
            text: post.caption.text,
            published_on: post.taken_at,
            id: post.id,
            pk: post.pk,
            code: post.code,
            username: post.user.username,
            user_pic: post.user.profile_pic_url,
            user_verified: post.user.is_verified,
            user_pk: post.user.pk,
            user_id: post.user.id,
            has_audio: post.has_audio,
            reply_count: view_replies_cta_string,
            like_count: post.like_count,
            images: post.carousel_media[].image_versions2.candidates[1].url,
            image_count: post.carousel_media_count,
            videos: post.video_versions[].url
        }""",
        data,
    )
    # Ensure videos are unique
    videos = list(set(result.get("videos") or []))
    # Process reply_count if it's not already an integer
    reply_count = result.get("reply_count")
    if reply_count and not isinstance(reply_count, int):
        try:
            reply_count = int(reply_count.split(" ")[0])
        except Exception:
            reply_count = 0
    else:
        reply_count = reply_count or 0

    # Build the post URL using the extracted code
    url = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
    posted_at = (
        datetime.fromtimestamp(result["published_on"])
        if result.get("published_on")
        else None
    )

    return ThreadsPost(
        post_id=result["id"],
        pk=result["pk"],
        code=result["code"],
        url=url,
        user_name=result["username"],
        content=result.get("text", ""),
        published_on=result["published_on"],
        posted_at=posted_at,
        reply_count=reply_count,
        like_count=result.get("like_count", 0),
        user_pic=result["user_pic"],
        user_verified=result["user_verified"],
        images=result.get("images", []),
        image_count=result.get("image_count", 0),
        videos=videos,
        has_audio=result.get("has_audio", False),
        user_pk=result["user_pk"],
        user_id=result.get("user_id"),
    )


def threads_posts_get(
    *, query: str, max_posts_number: int = 10
) -> Iterator[ThreadsPost]:
    """
    Fetch posts from Threads based on the given query using a hidden JSON dataset.
    """
    search_url = f"https://www.threads.net/search?q={query}&serp_type=default"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print(f"Searching for: {query}")
        page.goto(search_url)
        # Wait for search results to load
        page.wait_for_selector("[data-pressable-container=true]")
        page.wait_for_timeout(2000)

        # Extract hidden JSON datasets from the page
        selector = Selector(page.content())
        hidden_datasets = selector.css(
            'script[type="application/json"][data-sjs]::text'
        ).getall()
        print(f"Found {len(hidden_datasets)} hidden datasets")

        posts_found = 0
        # Iterate over the datasets to locate and parse thread items
        for hidden_dataset in hidden_datasets:
            if posts_found >= max_posts_number:
                break
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            if "thread_items" not in hidden_dataset:
                continue
            data = json.loads(hidden_dataset)
            thread_items = nested_lookup("thread_items", data)
            if not thread_items:
                continue
            for thread in thread_items:
                for t in thread:
                    if posts_found >= max_posts_number:
                        break
                    try:
                        yield parse_thread(t)
                        posts_found += 1
                    except Exception as e:
                        print(f"Error processing post: {str(e)}")
                        continue

        browser.close()


if __name__ == "__main__":
    # Example usage: search for posts related to "CBT therapy"
    results = threads_posts_get(query="Smart watches", max_posts_number=10)
    # Convert posts to a list of dictionaries and save to JSON
    posts_data = [vars(post) for post in results]
    with open("threads_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, default=str)
    print("Results saved to threads_posts.json")
