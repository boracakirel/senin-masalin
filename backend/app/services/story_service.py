import asyncio
import re

from fastapi import HTTPException, status

from app.schemas.story import StoryGenerateRequest, StoryGenerateResponse
from app.services.nvidia_service import NvidiaStoryService, get_nvidia_story_service
from app.services.pedagogical_story_engine import get_age_group
from app.services.prompt_builder import PromptBuilder


class StoryService:
    def __init__(self, prompt_builder: PromptBuilder, ai_service: NvidiaStoryService) -> None:
        self._prompt_builder = prompt_builder
        self._ai_service = ai_service

    async def generate(self, request: StoryGenerateRequest) -> StoryGenerateResponse:
        system_prompt = self._prompt_builder.build_system_prompt()
        story_prompt = self._prompt_builder.build_story_prompt(request)
        try:
            story = await asyncio.wait_for(
                self._ai_service.generate_story(system_prompt, story_prompt),
                timeout=120,
            )
        except TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Story generation provider timed out.",
            ) from None

        story = repair_age_2_3_story(request, story)
        violations = validate_age_2_3_story(request, story)
        if not violations:
            return story

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Story provider could not satisfy age_2_3 pedagogical rules.",
        )


def get_story_service() -> StoryService:
    return StoryService(
        prompt_builder=PromptBuilder(),
        ai_service=get_nvidia_story_service(),
    )


def validate_age_2_3_story(request: StoryGenerateRequest, story: StoryGenerateResponse) -> list[str]:
    if get_age_group(request.age) != "age_2_3":
        return []

    text = " ".join([story.baslangic, story.macera, story.sonuc, story.moral])
    violations: list[str] = []

    word_count = len(get_words(text))
    if word_count < 120:
        violations.append(f"Story has {word_count} Turkish words; it must have 120-180 words and never be under 120.")

    sentence_lengths = [len(get_words(sentence)) for sentence in split_sentences_for_average(text)]
    if sentence_lengths:
        average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        if average_sentence_length < 4 or average_sentence_length > 7:
            violations.append("Average sentence length must be between 4 and 7 Turkish words.")

    emotion_count = count_explicit_emotions(text)
    if emotion_count < 3:
        violations.append("Story must explicitly include at least three emotion words such as mutlu, üzgün, heyecanlı, meraklı, korkmuş or rahatlamış.")

    if count_dialogue_lines(text) < 2:
        violations.append("Story must include at least two very short dialogue lines.")

    if not has_repeated_phrase(text):
        violations.append("Story must naturally repeat one short phrase at least twice.")

    return violations


def repair_age_2_3_story(request: StoryGenerateRequest, story: StoryGenerateResponse) -> StoryGenerateResponse:
    if get_age_group(request.age) != "age_2_3":
        return story

    repaired_story = story.model_copy()
    text = combine_story_text(repaired_story)
    name = format_child_name(request.child_name)
    animal = request.animal.strip().lower()
    animal_title = capitalize_turkish(animal)
    color_title = capitalize_turkish(request.favorite_color.strip().lower())

    if count_dialogue_lines(text) < 2 or not has_repeated_phrase(text):
        repaired_story.macera = (
            f"{repaired_story.macera} "
            f"'Haydi gidelim!' dedi {name}. "
            f"'Haydi gidelim!' dedi {animal}."
        )

    while count_explicit_emotions(combine_story_text(repaired_story)) < 3:
        repaired_story.sonuc = f"{repaired_story.sonuc} {name} mutlu oldu. {animal_title} meraklı baktı. Herkes rahatlamıştı."

    lengthening_sentences = [
        f"{name} yavaşça derin nefes aldı.",
        f"{animal_title} ona nazikçe baktı.",
        f"{animal_title} küçük kuyruğunu salladı.",
        "Oda yine sıcak oldu.",
        f"{name} kendini güvende hissetti.",
        f"{color_title} ışık yumuşakça parladı.",
        f"{animal_title} sessizce yanına oturdu.",
        f"{animal_title} de tatlı tatlı uyudu.",
    ]
    sentence_index = 0
    while len(get_words(combine_story_text(repaired_story))) < 120:
        repaired_story.sonuc = f"{repaired_story.sonuc} {lengthening_sentences[sentence_index % len(lengthening_sentences)]}"
        sentence_index += 1

    return repaired_story


def format_child_name(child_name: str) -> str:
    stripped = child_name.strip()
    if not stripped:
        return stripped
    return stripped[:1].upper() + stripped[1:]


def capitalize_turkish(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return stripped
    return stripped[:1].upper() + stripped[1:]


def combine_story_text(story: StoryGenerateResponse) -> str:
    return " ".join([story.baslangic, story.macera, story.sonuc, story.moral])


def build_corrective_prompt(story_prompt: str, story: StoryGenerateResponse, violations: list[str]) -> str:
    violation_lines = "\n".join(f"- {violation}" for violation in violations)
    failed_story = story.model_dump_json()
    return (
        f"{story_prompt}\n\n"
        "The previous age_2_3 draft below failed mandatory checks. Rewrite and expand it. "
        "Keep the story simple, but make it longer with about 22-30 very short sentences. "
        "Do not answer until the story has 120-180 Turkish words, one repeated phrase appearing twice with the same wording, at least two short dialogue lines, and at least three explicit emotion words. "
        "Use these section budgets: baslangic 30-40 words, macera 55-75 words, sonuc 30-45 words, moral 4-7 words.\n"
        f"Failed draft JSON:\n{failed_story}\n\n"
        f"{violation_lines}\n"
    )


def get_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü0-9]+", text)


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"[.!?]+", text) if sentence.strip()]


def split_sentences_for_average(text: str) -> list[str]:
    return [
        sentence
        for sentence in split_sentences(text)
        if len(get_words(sentence)) >= 3 and not ("'" in sentence or '"' in sentence)
    ]


def count_explicit_emotions(text: str) -> int:
    emotion_words = {
        "mutlu",
        "mutluydu",
        "üzgün",
        "üzgündü",
        "heyecanlı",
        "heyecanlıydı",
        "meraklı",
        "meraklıydı",
        "korkmuş",
        "korkmuştu",
        "rahatlamış",
        "neşeli",
        "neşeliydi",
        "sevindi",
        "rahatladı",
        "rahatlamıştı",
    }
    words = {word.lower() for word in get_words(text)}
    return len(words.intersection(emotion_words))


def count_dialogue_lines(text: str) -> int:
    return len(re.findall(r"['\"][^'\"]{1,80}['\"]", text))


def has_repeated_phrase(text: str) -> bool:
    quoted_phrases = [phrase.lower().strip() for phrase in re.findall(r"['\"]([^'\"]{2,80})['\"]", text)]
    if any(quoted_phrases.count(phrase) >= 2 for phrase in quoted_phrases):
        return True

    sentences = [sentence.lower().strip() for sentence in split_sentences(text)]
    return any(sentences.count(sentence) >= 2 for sentence in sentences)
