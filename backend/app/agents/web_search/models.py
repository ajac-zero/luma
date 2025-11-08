from __future__ import annotations

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Individual search result from web search"""

    title: str
    url: str
    content: str
    score: float | None = None


class WebSearchState(BaseModel):
    """State passed to agent tools via deps"""

    user_query: str
    max_results: int = Field(default=5, ge=1, le=10)
    include_raw_content: bool = False


class WebSearchResponse(BaseModel):
    """Structured response from the web search agent"""

    query: str
    results: list[SearchResult]
    summary: str
    total_results: int
