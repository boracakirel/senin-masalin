from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TrimmedString = Annotated[str, Field(min_length=1, max_length=200)]
ThemeKey = Literal[
    "orman",
    "deniz_alti",
    "uzay",
    "dinozorlar",
    "prenses_ve_sato",
    "sihirli_dunya",
    "tek_boynuzlu_atlar",
    "ejderhalar",
    "periler",
    "korsanlar",
    "robotlar",
    "trenler",
    "ciftlik",
    "gokkusagi",
    "bulutlar",
    "karlar_ulkesi",
    "cicek_bahcesi",
    "kamp_macerasi",
    "gizemli_ada",
    "sirk",
]


class StoryGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    child_name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=2, le=12)]
    animal: Annotated[str, Field(min_length=1, max_length=100)]
    themes: Annotated[list[ThemeKey], Field(min_length=1, max_length=3)]
    favorite_color: Annotated[str, Field(min_length=1, max_length=100)]

    @field_validator("child_name", "animal", "favorite_color")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped


class StoryGenerateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    baslangic: str
    macera: str
    sonuc: str
    moral: str
