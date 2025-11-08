from __future__ import annotations

from .agent import agent
from .models import WebSearchResponse, WebSearchState


async def search_web(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
) -> WebSearchResponse:
    """
    Execute web search using Tavily MCP server.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-10)
        include_raw_content: Whether to include full content in results

    Returns:
        WebSearchResponse with results and summary
    """
    state = WebSearchState(
        user_query=query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )

    prompt = (
        f"Search the web for: {query}\n\n"
        f"Return the top {max_results} most relevant results. "
        "Provide a concise summary of the key findings."
    )

    # Ejecutar agente con Tavily API directa
    result = await agent.run(prompt, deps=state)
    return result.output
