from pydantic import BaseModel


class Score(BaseModel):
    score: int

    def __init__(self, score: int):
        super().__init__(**{"score": score})
