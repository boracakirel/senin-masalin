import json

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.story import StoryGenerateResponse


class NvidiaStoryService:
    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.nvidia_api_key
        self._api_url = settings.nvidia_api_url
        self._model = settings.nvidia_model

    async def generate_story(self, system_prompt: str, story_prompt: str) -> StoryGenerateResponse:
        if not self._api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NVIDIA_API_KEY is not configured.",
            )

        try:
            content = await self._request_story(system_prompt, story_prompt)
            return StoryGenerateResponse.model_validate_json(extract_json_object(content))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="NVIDIA returned an invalid story format.",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise map_nvidia_error(exc) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Story generation provider failed.",
            ) from exc

    async def _request_story(self, system_prompt: str, story_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": story_prompt},
            ],
            "max_tokens": 700,
            "temperature": 0.8,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(self._api_url, headers=headers, json=payload)
            response.raise_for_status()

        return extract_message_content(response.json())


def parse_stream_content(line: str) -> str:
    if not line or not line.startswith("data: "):
        return ""

    data = line.removeprefix("data: ").strip()
    if data == "[DONE]":
        return ""

    payload = json.loads(data)
    choices = payload.get("choices", [])
    if not choices:
        return ""

    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    return content if isinstance(content, str) else ""


def extract_message_content(payload: dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")
    return content if isinstance(content, str) else ""


def extract_json_object(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("No JSON object found", stripped, 0)

    return stripped[start : end + 1]


def map_nvidia_error(exc: httpx.HTTPStatusError) -> HTTPException:
    status_code = exc.response.status_code
    if status_code in {401, 403}:
        detail = "NVIDIA API key is invalid or unauthorized."
    elif status_code == 429:
        detail = "NVIDIA quota or rate limit was reached. Check your NVIDIA API credits and limits."
    elif 400 <= status_code < 500:
        detail = "NVIDIA rejected the story generation request. Check NVIDIA_MODEL and request settings."
    else:
        detail = "Story generation provider failed."

    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


def get_nvidia_story_service() -> NvidiaStoryService:
    return NvidiaStoryService()
