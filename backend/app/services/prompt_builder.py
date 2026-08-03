from app.schemas.story import StoryGenerateRequest
from app.services.pedagogical_story_engine import PedagogicalStoryEngine


class PromptBuilder:
    def __init__(self, pedagogical_engine: PedagogicalStoryEngine | None = None) -> None:
        self._pedagogical_engine = pedagogical_engine or PedagogicalStoryEngine()

    def build_system_prompt(self) -> str:
        return (
            "Senin Masalın story generation service. Follow the backend/rules YAML context. "
            "Return only one valid JSON object with exactly these string keys: "
            "title, baslangic, macera, sonuc, moral. Do not use Markdown. Do not add explanations."
        )

    def build_story_prompt(self, request: StoryGenerateRequest) -> str:
        pedagogical_context = self._pedagogical_engine.build_prompt_context(request)
        return (
            f"{pedagogical_context}\n\n"
            "Generate a personalized story using these child inputs.\n\n"
            f"Çocuğun adı: {request.child_name}\n"
            f"Yaşı: {request.age}\n"
            f"Sevdiği hayvan: {request.animal}\n"
            f"Sevdiği renk: {request.favorite_color}\n"
            f"Seçilen tema anahtarları: {', '.join(request.themes)}\n"
            "\nThe generated story must satisfy the selected age, developmental, story and theme rules above.\n"
            "\nOutput format is mandatory. Return only this JSON shape, with Turkish story text as string values:\n"
            '{"title":"...","baslangic":"...","macera":"...","sonuc":"...","moral":"..."}\n'
            "No Markdown, no headings, no commentary, no text before or after the JSON.\n"
        )
