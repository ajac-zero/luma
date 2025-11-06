from fastapi import APIRouter
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)
model = OpenAIChatModel(model_name="gpt-4o", provider=provider)
agent = Agent(model=model)

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])


@router.post("/chat")
async def chat(request: Request) -> Response:
    return await VercelAIAdapter.dispatch_request(request, agent=agent)
