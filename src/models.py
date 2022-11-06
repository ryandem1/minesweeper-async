import uuid

from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Generator


class Score(BaseModel):
    score: int

    def __init__(self, score: int):
        super().__init__(**{"score": score})


class BoardSpaceType(StrEnum):
    BLANK = "BLANK"  # Non-mine space with no mines in immediate proximity
    VALUE = "VALUE"  # Non-mine space with at least 1 mine in immediate proximity
    MINE = "MINE"  # Mine space


class BoardSpace(BaseModel):
    x: int
    y: int
    value: int  # Number of mines in immediate proximity of space
    type_: BoardSpaceType
    hit: bool = False  # Whether the space has been hit or not


class Board(BaseModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    spaces: list[BoardSpace]

    # Board dimensions
    length: int = 9
    height: int = 9

    def __getitem__(self, item: tuple[int, int]) -> BoardSpace:
        """
        Gets board space by x, y coordinates.

        Parameters
        ----------
        item : tuple[int, int]
            x,y coordinates of space to get

        Returns
        -------
        space : BoardSpace
            Space at coordinates
        """
        if not self.length > item[0] > 0 or not self.height > item[1] > 0:
            raise IndexError(f"Coordinates: {item} out-of-range. Board dimensions: {self.length}x{self.height}")

        space = next((s for s in self.spaces if s.x == item[0] and s.y == item[1]), None)
        if not space:
            raise ValueError(
                f"Somehow don't have space for coordinates: {item} even though it is in range of "
                f"{self.length}x{self.height} board"
            )

        return space

    def __iter__(self) -> Generator[BoardSpace, None, None]:
        """
        Iterates through the ``BoardSpace`` objects in ``self.spaces``. Order is not guaranteed to be in any way.

        Returns
        -------
        BoardSpace generator
        """
        for space in self.spaces:
            yield space
