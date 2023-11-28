from typing import Optional, Type, List

from langchain.tools import BaseTool
from pydantic import BaseModel
from app.models import Stories, Comments

from app.functions import get_hn_stories
from app.functions import get_relevant_comments


class StoriesTool(BaseTool):
    name = "get_stories"
    description = "Gets stories from Hacker News"

    def _run(self, limit: int = 5, keywords: List[str] = None, story_type: str = "top"):
        stories = get_hn_stories(limit, keywords, story_type)
        return stories

    def _arun(self, limit: int = 5, keywords: List[str] = None, story_type: str = "top"):
        stories = get_hn_stories(limit, keywords, story_type)
        return stories

    args_schema: Optional[Type[BaseModel]] = Stories


class CommentsTool(BaseTool):
    name = "get_comments"
    description = "Gets comments from a specific Hacker News story"

    def _run(self, story_id: int, limit: int = 10):
        comments = get_relevant_comments(story_id, limit)
        return comments

    def _arun(self, story_id: int, limit: int = 10):
        comments = get_relevant_comments(story_id, limit)
        return comments

    args_schema: Optional[Type[BaseModel]] = Comments
