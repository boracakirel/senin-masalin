from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Story(SQLModel, table=True):
    __tablename__ = "stories"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(max_length=100, index=True)
    age: int = Field(ge=2, le=12)
    animal: str = Field(max_length=100)
    themes: str = Field(max_length=500)
    favorite_color: str = Field(max_length=100)
    title: str = Field(max_length=255)
    baslangic: str = Field(sa_column=Column(Text, nullable=False))
    macera: str = Field(sa_column=Column(Text, nullable=False))
    sonuc: str = Field(sa_column=Column(Text, nullable=False))
    moral: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
