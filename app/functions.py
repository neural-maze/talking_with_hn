import asyncio
import aiohttp
from typing import List, Dict, Union

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


async def fetch_story_ids(story_type: str = "top"):
    """
    Asynchronously fetches the top story IDs.

    Args:
        story_type: The story type. Defaults to top (`topstories.json`)

    Returns:
        List[int]: A list of top story IDs.
    """
    url = f"{BASE_URL}/topstories.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            top_story_ids = await response.json()

    return top_story_ids


async def get_top_hn_stories(keywords: str = None, limit: int = 5):
    """
    Asynchronously fetches the top Hacker News stories based on the provided parameters.

    Parameters:
    - keyword (str): A keyword to filter the top stories.
    - limit (int): The number of top stories to retrieve. Default is 5.

    Returns:
    - List[Dict[str, Union[str, int]]]: A list of dictionaries containing
      'title', 'url', and 'score' of top stories.
    """
    top_story_ids = await fetch_story_ids()

    async def fetch_and_filter_stories(story_id):
        async with aiohttp.ClientSession() as session:
            story = await fetch_item(session, story_id)
        return story

    tasks = [fetch_and_filter_stories(story_id) for story_id in top_story_ids]
    top_stories = await asyncio.gather(*tasks)

    filtered_stories = []
    for story in top_stories:
        story_info = {
            "title": story.get("title"),
            "url": story.get("url"),
            "score": story.get("score"),
        }

        if keywords is None or any(keyword.lower() in story['title'].lower() for keyword in keywords):
            filtered_stories.append(story_info)

    return filtered_stories[:limit]