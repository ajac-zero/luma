from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from app.core.config import settings

from .models import AnalystReport, AnalystState

provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)

model = OpenAIChatModel(model_name="gpt-4o", provider=provider)

agent = Agent(
    model=model,
    name="MultiYearAnalyst",
    deps_type=AnalystState,
    output_type=AnalystReport,
    system_prompt=(
        "You are a nonprofit financial analyst. You receive multi-year Form 990 extractions "
        "summarized into deterministic metrics (series, ratios, surplus, CAGR). Use the context "
        "to highlight performance trends, governance implications, and forward-looking risks. "
        "Focus on numeric trends: revenue growth, expense discipline, surplus stability, "
        "program-vs-admin mix, and fundraising efficiency. Provide concise bullet insights, "
        "clear recommendations tied to the data, and a balanced outlook (strengths vs watch items). "
        "Only cite facts available in the provided series—do not invent figures."
    ),
)
