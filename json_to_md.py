import json
import re


def clean_reddit_formatting(text):
    """
    Clean Reddit-specific formatting from the text.
    """
    # Replace Reddit's line break marker
    text = text.replace("&#x200B;", "")

    # Replace encoded emojis with their Unicode equivalents
    emoji_map = {
        "\\ud83e\\udd70": "🥰",
        "\\ud83d\\ude0d": "😍",
        "\\ud83d\\ude18": "😘",
        "\\ud83d\\ude0f": "😏",
        "\\ud83d\\ude09": "😉",
        "\\u2764\\ufe0f": "❤️",
        "\\ud83d\\udd25": "🔥",
        "\\ud83c\\udf46": "🍆",
    }

    for encoded, unicode in emoji_map.items():
        text = text.replace(encoded, unicode)

    # Remove any remaining escape sequences
    text = re.sub(r"\\[a-z0-9]{4}", "", text)

    return text


def json_to_markdown(json_data):
    """
    Convert JSON data to markdown format.
    """
    markdown_content = []

    for post in json_data:
        print(post)
        print("post--------------")
        # Add title as main heading
        if "title" in post:
            markdown_content.append(f"# {post['title']}\n")

        # Add content if available
        if "content" in post:
            # Clean the content
            content = clean_reddit_formatting(post["content"])
            markdown_content.append(content)

        # Add source URL if available
        if "url" in post:
            markdown_content.append(f"\n\nSource: {post['url']}\n")

        # Add metadata if available
        if "is_relevant" in post:
            markdown_content.append(
                f"\nRelevance: {'Yes' if post['is_relevant'] else 'No'}"
            )

        if "relevance_score" in post:
            markdown_content.append(f"Relevance Score: {post['relevance_score']}")

        # Add separator between posts
        markdown_content.append("\n---\n")

    return "\n".join(markdown_content)


def convert_file(input_file, output_file):
    """
    Convert a JSON file to a markdown file.

    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output markdown file
    """
    try:
        # Read JSON file
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        print(f"Successfully read {input_file}")
        print(f"Converting {len(json_data)} posts to markdown...")

        # Convert to markdown
        markdown_content = json_to_markdown(json_data)

        # Write markdown file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Successfully converted {input_file} to {output_file}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    convert_file("reddit_relevance_output.json", "output.md")
