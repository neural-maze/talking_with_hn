from bs4 import BeautifulSoup
import asyncio
import aiohttp
from typing import List, Dict, Union
import json

BASE_URL = "https://hacker-news.firebaseio.com/v0"


async def fetch_item(session: aiohttp.ClientSession, item_id: int):
    """
    Asynchronously fetches details of a story by its ID.

    Args:
        session: Aiohttp ClientSession for making HTTP requests.
        item_id (int): The ID of the item to fetch.

    Returns:
        dict: Details of the story.
    """
    url = f"{BASE_URL}/item/{item_id}.json"
    async with session.get(url) as response:
        return await response.json()


async def fetch_story_ids(story_type: str = "top", limit: int = None):
    """
    Asynchronously fetches the top story IDs.

    Args:
        story_type: The story type. Defaults to top (`topstories.json`)
        limit: The limit of stories to be fetched.

    Returns:
        List[int]: A list of top story IDs.
    """
    url = f"{BASE_URL}/{story_type}stories.json"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(url) as response:
            story_ids = await response.json()

    if limit:
        story_ids = story_ids[:limit]

    return story_ids


async def fetch_text(session, url):
    """
    Fetches the text from a URL (if there's text to be fetched). If it fails,
    it will return an informative message to the LLM.

    Args:
        session: `aiohttp` session
        url: The story URL

    Returns:
        A string representing whether the story text or an informative error (represented as a string)
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:

                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text()

                return text_content
            else:
                return f"Unable to fetch content from {url}. Status code: {response.status}"
    except Exception as e:
        return f"An error occurred: {e}"


async def get_hn_stories(limit: int = 5, keywords: List[str] = None, story_type: str = "top"):
    """
    Asynchronously fetches the top Hacker News stories based on the provided parameters.

    Args:
        limit (int): The number of top stories to retrieve. Default is 10.
        keywords (List[str]): A list of keywords to filter the top stories.
        story_type (str): The story type

    Returns:
        List[Dict[str, Union[str, int]]]: A list of dictionaries containing
        'id', 'title', 'url', and 'score' of the stories.
    """

    if limit and keywords is None:
        story_ids = await fetch_story_ids(story_type, limit)
    else:
        story_ids = await fetch_story_ids(story_type)

    async def fetch_and_filter_stories(story_id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            story = await fetch_item(session, story_id)
        return story

    tasks = [fetch_and_filter_stories(story_id) for story_id in story_ids]
    stories = await asyncio.gather(*tasks)

    filtered_stories = []
    for story in stories:
        story_info = {
            "story_id": story.get("id"),
            "title": story.get("title"),
            "url": story.get("url"),
            "score": story.get("score"),
        }

        if keywords is None or any(keyword.lower() in story['title'].lower() for keyword in keywords):
            filtered_stories.append(story_info)

    return filtered_stories[:limit]


async def get_relevant_comments(story_id: int, limit: int =10):
    """
    Get the most relevant comments for a Hacker News item.

    Args:
        story_id: The ID of the Hacker News item.
        limit: The number of comments to retrieve (default is 10).

    Returns:
        A list of dictionaries, each containing comment details.
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        story = await fetch_item(session, story_id)

        if 'kids' not in story:
            return "This item doesn't have comments."

        comment_ids = story['kids']

        comment_details = await asyncio.gather(*[fetch_item(session, cid) for cid in comment_ids])
        comment_details.sort(key=lambda comment: comment.get('score', 0), reverse=True)

        relevant_comments = comment_details[:limit]
        relevant_comments = [comment["text"] for comment in relevant_comments]

        return json.dumps(relevant_comments)


async def get_story_content(story_url: str):
    """
    Gets the content of the story using BeautifulSoup.

    Args:
        story_url: A string representing the story URL

    Returns:
        The content of the story
    """
    async with aiohttp.ClientSession() as session:
        story_content = await fetch_text(session, story_url)
        return story_content
