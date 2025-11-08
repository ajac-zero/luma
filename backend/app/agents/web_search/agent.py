from __future__ import annotations

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from tavily import TavilyClient

from app.core.config import settings

from .models import WebSearchResponse, WebSearchState, SearchResult


provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)
model = OpenAIChatModel(model_name="gpt-4o", provider=provider)


tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

agent = Agent(
    model=model,
    name="WebSearchAgent",
    deps_type=WebSearchState,
    output_type=WebSearchResponse,
    system_prompt=(
        "You are a web search assistant powered by Tavily. "
        "Use the tavily_search tool to find relevant, up-to-date information. "
        "Return a structured WebSearchResponse with results and a concise summary. "
        "Always cite your sources with URLs."
    ),
)


@agent.tool
def tavily_search(ctx: RunContext[WebSearchState], query: str) -> list[SearchResult]:
    """Search the web using Tavily API for up-to-date information."""
    response = tavily_client.search(
        query=query,
        max_results=ctx.deps.max_results,
        search_depth="basic",
        include_raw_content=ctx.deps.include_raw_content,
    )

    results = []
    for item in response.get("results", []):
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
                score=item.get("score"),
            )
        )

    return results


@agent.output_validator
def finalize_response(
    ctx: RunContext[WebSearchState],
    response: WebSearchResponse,
) -> WebSearchResponse:
    """Post-process and validate the search response"""
    return response.model_copy(
        update={
            "query": ctx.deps.user_query,
            "total_results": len(response.results),
        }
    )
