from typing import List
from pydantic import BaseModel, Field


class Stories(BaseModel):
    """A model representing the top stories from Hacker News"""
    limit: int = Field(default=5, description="The number of stories to return. Defaults to 5.")
    keywords: List[str] = Field(default=None, description="The list of keywords to filter the stories. "
                                                          "Defaults to None")
    story_type: str = Field(default="top", description="The story type. It can be one of the following: "
                                                       "'top', 'new', 'best', 'ask', 'show', 'job'. Defaults to 'top'")


class Item(BaseModel):
    """A model representing a story, comment, job, Ask HN and even a poll"""
    item_id: str = Field(..., description="The item's unique id")

