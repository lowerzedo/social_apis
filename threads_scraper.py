import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright

def parse_thread(data: Dict) -> Dict:
    """Parse Threads post JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
            text: post.caption.text,
            published_on: post.taken_at,
            id: post.id,
            username: post.user.username,
            user_pic: post.user.profile_pic_url,
            user_verified: post.user.is_verified,
            like_count: post.like_count,
            images: post.carousel_media[].image_versions2.candidates[1].url,
            videos: post.video_versions[].url
        }""",
        data,
    )
    result["videos"] = list(set(result["videos"] or []))
    result["url"] = f"https://www.threads.net/@{result['username']}/post/{result['id']}"
    return result

def search_threads(keywords: list[str], output_file: str = None) -> dict:
    """Search Threads posts by keywords"""
    search_term = " ".join(keywords)
    search_url = f"https://www.threads.net/search?q={search_term}&serp_type=default"
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print(f"Searching for: {search_term}")
        page.goto(search_url)
        
        # Wait for search results to load
        page.wait_for_selector("[data-pressable-container=true]")
        page.wait_for_timeout(2000)

        # Extract hidden JSON datasets
        selector = Selector(page.content())
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        print(f"Found {len(hidden_datasets)} hidden datasets")

        all_threads = []
        
        # Find and parse the dataset containing thread data
        for hidden_dataset in hidden_datasets:
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            data = json.loads(hidden_dataset)
            thread_items = nested_lookup("thread_items", data)
            
            if not thread_items:
                continue

            # Parse thread data
            threads = [parse_thread(t) for thread in thread_items for t in thread]
            all_threads.extend(threads)

        result = {
            "search_term": search_term,
            "threads": all_threads,
            "total_results": len(all_threads)
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        return result

# Example usage
if __name__ == "__main__":
    keywords = ["python", "coding"]
    output_file = "search_results.json"
    result = search_threads(keywords, output_file)
    print(f"Found {result['total_results']} threads")
    print(f"Results saved to {output_file}")