import json
import logging
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Header
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from starlette.requests import Request
from starlette.responses import Response

from app.agents import analyst, form_auditor, web_search
from app.core.config import settings
from app.services.extracted_data_service import get_extracted_data_service

provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)
model = OpenAIChatModel(model_name="gpt-4o", provider=provider)


@dataclass
class Deps:
    extracted_data: list[dict[str, Any]]


agent = Agent(model=model, deps_type=Deps)

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])

logger = logging.getLogger(__name__)


@agent.tool
async def build_audit_report(ctx: RunContext[Deps]):
    """Calls the audit subagent to get a full audit report of the organization"""
    data = ctx.deps.extracted_data[0]

    result = await form_auditor.build_audit_report(data)

    return result.model_dump()


@agent.tool
async def build_analysis_report(ctx: RunContext[Deps]):
    """Calls the analyst subagent to get a full report of the organization's performance across years"""
    data = ctx.deps.extracted_data
    if not data:
        raise ValueError("No extracted data available for analysis.")

    if len(data) == 1:
        logger.info(
            "build_analysis_report called with single-year data; report will still be generated but trends may be limited."
        )

    result = await analyst.build_performance_report(data)

    return result.model_dump()


@agent.tool_plain
async def search_web_information(query: str, max_results: int = 5):
    """Search the web for up-to-date information using Tavily. Use this when you need current information, news, research, or facts not in your knowledge base."""
    result = await web_search.search_web(query=query, max_results=max_results)

    return result.model_dump()


@router.post("/chat")
async def chat(request: Request, tema: Annotated[str, Header()]) -> Response:
    extracted_data_service = get_extracted_data_service()

    data = await extracted_data_service.get_by_tema(tema)

    extracted_data = [doc.get_extracted_data() for doc in data]

    logger.info(f"Extracted data amount: {len(extracted_data)}")

    deps = Deps(extracted_data=extracted_data)

    return await VercelAIAdapter.dispatch_request(request, agent=agent, deps=deps)
