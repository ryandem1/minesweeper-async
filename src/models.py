import uuid

from pydantic import BaseModel, Field


class Score(BaseModel):
    score: int

    def __init__(self, score: int):
        super().__init__(**{"score": score})


class Board(BaseModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
