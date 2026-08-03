from fastapi import APIRouter, Depends

from app.schemas.story import StoryGenerateRequest, StoryGenerateResponse
from app.services.story_service import StoryService, get_story_service


router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.post("/generate", response_model=StoryGenerateResponse)
async def generate_story(
    request: StoryGenerateRequest,
    story_service: StoryService = Depends(get_story_service),
) -> StoryGenerateResponse:
    return await story_service.generate(request)
