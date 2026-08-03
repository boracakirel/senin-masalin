import yaml

from app.core.paths import RULES_DIR
from app.schemas.story import StoryGenerateRequest


class PedagogicalStoryEngine:
    def build_prompt_context(self, request: StoryGenerateRequest) -> str:
        age_group = get_age_group(request.age)
        age_rules = self._load_yaml_file("age_rules.yaml")["age_groups"][age_group]
        story_rules = self._load_yaml_file("story_rules.yaml")
        theme_rules = self._load_yaml_file("theme_rules.yaml")
        developmental_outcomes = self._load_developmental_outcomes(age_group)
        selected_themes = [theme_rules["themes"][theme_key] for theme_key in request.themes]
        compact_rules = {
            "age_group": age_group,
            "developmental_outcomes": developmental_outcomes,
            "age_rules": {
                "goal": age_rules.get("developmental_goal"),
                "length": age_rules.get("recommended_story_length"),
                "minimum_length": age_rules.get("minimum_story_length"),
                "section_word_targets": age_rules.get("section_word_targets"),
                "sentences": [
                    age_rules.get("sentence_length_guidance"),
                    age_rules.get("sentence_count_guidance"),
                    age_rules.get("sentence_complexity", {}).get("required"),
                ],
                "conflict": [
                    age_rules.get("conflict_complexity"),
                    age_rules.get("problem_timing"),
                    age_rules.get("problem_clarity"),
                ],
                "emotions": age_rules.get("emotional_explicitness"),
                "repetition": age_rules.get("repetition"),
                "dialogue": age_rules.get("dialogue"),
                "fantasy": age_rules.get("fantasy_level", {}).get("rule", age_rules.get("fantasy_level")),
                "characters": age_rules.get("characters"),
                "resolution": age_rules.get("resolution"),
                "moral": age_rules.get("moral"),
                "vocabulary": age_rules.get("vocabulary_level"),
            },
            "story_rules": {
                "structure": story_rules["structure"],
                "must": [
                    story_rules["rules"]["one_dramatic_question"],
                    story_rules["rules"]["one_central_conflict_for_younger_children"],
                    story_rules["rules"]["positive_resolution"],
                    story_rules["rules"]["indirect_moral_message"],
                    story_rules["rules"]["good_pacing"],
                ],
                "output_contract": story_rules["output_contract"],
            },
            "theme_rules": {
                "selection": theme_rules["selection_rules"],
                "selected_themes": selected_themes,
            },
        }
        return (
            "Pedagojik Masal Motoru kuralları aşağıdadır. Kurallar backend/rules YAML dosyalarından seçilmiştir.\n"
            + yaml.safe_dump(compact_rules, allow_unicode=True, sort_keys=False).strip()
        )

    def _load_yaml_file(self, file_name: str) -> dict:
        path = RULES_DIR / file_name
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def _load_developmental_outcomes(self, age_group: str) -> dict:
        data = self._load_yaml_file("developmental_outcomes.yaml")
        return data["developmental_outcomes"][age_group]

    def _load_selected_age_rules(self, age_group: str) -> dict:
        data = self._load_yaml_file("age_rules.yaml")
        return {age_group: data["age_groups"][age_group]}

    def build_selected_age_checklist(self, request: StoryGenerateRequest) -> str:
        age_group = get_age_group(request.age)
        return yaml.safe_dump(self._load_selected_age_rules(age_group), allow_unicode=True, sort_keys=False).strip()

    def _load_selected_theme_rules(self, theme_keys: list[str]) -> dict:
        data = self._load_yaml_file("theme_rules.yaml")
        selected_themes = {theme_key: data["themes"][theme_key] for theme_key in theme_keys}
        return {
            "selection_rules": data["selection_rules"],
            "themes": selected_themes,
        }

    def _load_story_rules(self) -> dict:
        data = self._load_yaml_file("story_rules.yaml")
        return {
            "structure": data["structure"],
            "rules": data["rules"],
            "output_contract": data["output_contract"],
        }


def get_age_group(age: int) -> str:
    if age <= 3:
        return "age_2_3"
    if age <= 5:
        return "age_4_5"
    if age <= 8:
        return "age_6_8"
    return "age_9_12"
