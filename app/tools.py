from typing import Optional, Type, List

from langchain.tools import BaseTool
from pydantic import BaseModel
from app.models import Stories

from app.functions import get_hn_stories


class StoriesTool(BaseTool):
    name = "get_stories"
    description = "Gets stories from Hacker News"

    def _run(self, limit: int = 10, keywords: List[str] = None, story_type: str = "top"):
        stories = get_hn_stories(limit, keywords, story_type)
        return stories

    def _arun(self, limit: int = 10, keywords: List[str] = None, story_type: str = "top"):
        stories = get_hn_stories(limit, keywords, story_type)
        return stories

    args_schema: Optional[Type[BaseModel]] = Stories
