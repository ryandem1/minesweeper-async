import uuid
import random
import itertools

from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Generator
from settings import BoardSettings


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
    value: int | None  # Number of mines in immediate proximity of space. None if space is a mine
    type_: BoardSpaceType
    hit: bool = False  # Whether the space has been hit or not


class Board(BaseModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    spaces: list[BoardSpace] = []
    settings: BoardSettings  # Most likely global board settings

    @classmethod
    def new(cls, settings: BoardSettings):
        """
        Creates a new randomized Minesweeper board. Randomness based on ``self.id``

        Returns
        -------
        Board object
        """
        obj = cls(settings=settings)
        random.seed(obj.id.int)

        # Adds bombs randomly on 2d plane of default dimensions
        available_coordinates = list(itertools.product(range(settings.length), range(settings.height)))
        obj.spaces.extend(
            BoardSpace(**{
                "x": coords[0],
                "y": coords[1],
                "value": None,
                "type_": BoardSpaceType.MINE
            })
            for coords in [
                available_coordinates.pop(random.randrange(len(available_coordinates)))
                for _ in range(settings.mines)
            ]
        )

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
        if not self.settings.length > item[0] > 0 or not self.settings.height > item[1] > 0:
            raise IndexError(
                f"Coordinates: {item} out-of-range. Board dimensions: {self.settings.length}x{self.settings.height}"
            )

        space = next((s for s in self.spaces if s.x == item[0] and s.y == item[1]), None)
        if not space:
            raise ValueError(
                f"Somehow don't have space for coordinates: {item} even though it is in range of "
                f"{self.settings.length}x{self.settings.height} board"
            )

        return space

    def __iter__(self) -> Generator[BoardSpace, None, None]:
        """
        Iterates through the ``BoardSpace`` objects in ``self.spaces``. Iterates starting from 0, 0. Iterates through
        all y's then all x's

        Returns
        -------
        BoardSpace generator
        """
        for coords in itertools.product(range(self.settings.length), range(self.settings.height)):
            space = next((s for s in self.spaces if s.x == coords[0] and s.y == coords[1]), None)
            if not space:
                raise ValueError(
                    f"Somehow don't have space for coordinates: {coords} even though it is in range of "
                    f"{self.settings.length}x{self.settings.height} board"
                )

            yield space
