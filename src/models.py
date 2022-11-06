import itertools
import random
import uuid
from enum import StrEnum
from typing import Generator, Any

from pydantic import BaseModel, Field

from settings import BoardSettings


class Score(BaseModel):
    score: int

    def __init__(self, score: int):
        super().__init__(score=score)


class Answer(BaseModel):
    answer: Any

    def __init__(self, answer: Any):
        super().__init__(answer=answer)


class BoardSpaceType(StrEnum):
    """
    The types that a ``BoardSpace`` could be
    """
    BLANK = "BLANK"  # Non-mine space with no mines in immediate proximity
    VALUE = "VALUE"  # Non-mine space with at least 1 mine in immediate proximity
    MINE = "MINE"  # Mine space


class BoardSpace(BaseModel):
    """
    A single Minesweeper space on a board. This serves as the representation of a space and the request body that a
    caller must send to reference a space on the board. Callers will typically send ``BoardSpace`` objects consisting
    of only an x, y coordinate value.
    """
    x: int
    y: int
    value: int | None = None  # Number of mines in immediate proximity of space.
    type: BoardSpaceType | None = None
    hit: bool | None = None
    flagged: bool | None = None


class Board(BaseModel):
    """
    Represents a single Minesweeper board. Takes in ``BoardSettings`` to determine mines/dimensions
    """
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    spaces: list[BoardSpace] | None = None
    settings: BoardSettings | None = None  # Most likely global board settings

    def __str__(self) -> str:
        """
        Prints a textual/graphical representation of the Minesweeper board. This really assumes that the print font will
        be monospace. If it isn't, it will be... ugly.

        Returns
        -------
        Monospace textart representation of Minesweeper board
        """
        output = ""
        current_x = 0

        for space in self:
            if current_x != space.x:
                output += "\n"
                current_x = space.x

            match space:
                case BoardSpace(type=BoardSpaceType.BLANK):
                    output += " _ "
                case BoardSpace(type=BoardSpaceType.VALUE) as space:
                    output += " " + str(space.value) + " "
                case BoardSpace(type=BoardSpaceType.MINE):
                    output += " * "
                case _:
                    raise ValueError(f"Unhandled type: {space.type}")
        return output

    def __getitem__(self, item: tuple[int, int] | BoardSpace) -> BoardSpace:
        """
        Gets board space by x, y coordinates.

        Parameters
        ----------
        item : tuple[int, int] | BoardSpace
            x,y coordinates of space to get. Can also pass in a ``BoardSpace`` object, and it will use the x/y values
            from there.

        Returns
        -------
        space : BoardSpace
            Space at coordinates
        """
        match item:
            case int(x), int(y):
                x, y = x, y
            case BoardSpace() as space:
                x, y = space.x, space.y
            case _:
                raise KeyError("Can only index into board with a pair of coords or a `BoardSpace`!")

        if not self.settings.length > x >= 0 or not self.settings.height > y >= 0:
            raise IndexError(
                f"Coordinates: {x, y} out-of-range. Board dimensions: {self.settings.length}x{self.settings.height}"
            )

        space = next((s for s in self.spaces if s.x == x and s.y == y), None)
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
        for x, y in itertools.product(range(self.settings.length), range(self.settings.height)):
            space = next((s for s in self.spaces if s.x == x and s.y == y), None)
            if not space:
                raise ValueError(
                    f"Somehow don't have space for coordinates: {x, y} even though it is in range of "
                    f"{self.settings.length}x{self.settings.height} board"
                )

            yield space

    @property
    def is_correct(self) -> bool:
        """
        Will check if:

        1. All mines are flagged
        2. All safe spaces are hit

        Returns
        -------
        result : bool
            True if the board is currently correct, False if not
        """
        all_mines_are_flagged = all(
            space.flagged
            for space in self
            if space.type == BoardSpaceType.MINE
        )
        all_safe_spaces_are_hit = all(
            space.hit
            for space in self
            if space.type != BoardSpaceType.MINE
        )

        return all_mines_are_flagged and all_safe_spaces_are_hit

    @classmethod
    def new(cls, settings: BoardSettings):
        """
        Creates a new randomized Minesweeper board. Randomness based on ``self.id``

        Returns
        -------
        Board object
        """
        obj = cls(spaces=[], settings=settings)
        random.seed(obj.id.int)

        # Adds mines randomly on 2d plane of dimensions specified in settings
        available_coordinates = list(itertools.product(range(settings.length), range(settings.height)))
        obj.spaces.extend(
            BoardSpace(
                x=x,
                y=y,
                value=1,  # For obfuscation,
                type=BoardSpaceType.MINE,
                hit=False,
                flagged=False
            )
            for x, y in [
                available_coordinates.pop(random.randrange(len(available_coordinates)))
                for _ in range(settings.mines)
            ]
        )

        # Adds value spaces according to mine neighbors
        mine_spaces = (space for space in obj.spaces if space.type == BoardSpaceType.MINE)
        for mine_space in mine_spaces:
            for neighbor in obj.get_neighbors(mine_space):
                match neighbor:
                    # If there is already a node created at the neighboring spot, increment the nearby-mine value
                    case BoardSpace() as space:
                        space.value += 1
                    case int(x), int(y):  # If x, y coords get returned, then the space has not been created yet
                        obj.spaces.append(
                            BoardSpace(
                                x=x,
                                y=y,
                                value=1,
                                type=BoardSpaceType.VALUE,
                                hit=False,
                                flagged=False
                            )
                        )
                        available_coordinates.remove((x, y))
                    case _:
                        raise ValueError(f"Unexpected neighbor value: {neighbor}")

        # Adds remaining blank spaces
        obj.spaces.extend(
            BoardSpace(
                x=x,
                y=y,
                value=0,
                type=BoardSpaceType.BLANK,
                hit=False,
                flagged=False
            )
            for x, y in available_coordinates
        )
        return obj

    def get_neighbors(self, space: BoardSpace) -> Generator[BoardSpace | tuple[int, int], None, None]:
        """
        Gets all neighbors for a given space. By definition, a space can have a maximum of 8 neighbors and a minimum of
        3 (if the space is in a corner).

        Parameters
        ----------
        space : BoardSpace
            Space on the current board to get neighbors for.

        Returns
        -------
        Generator of neighboring ``BoardSpace`` objects. Returns neighbor nodes starting from the immediate left
        neighbor, and then rotating clockwise. If there is no ``BoardSpace`` at a neighbors coordinates and the coords
        are in range, this will instead return the coordinates. See ``self.new`` for use
        """
        for neighbor_coords in itertools.product(range(space.x - 1, space.x + 2), range(space.y - 1, space.y + 2)):
            try:
                yield self[neighbor_coords]
            except IndexError:  # Current node must be an edge, so neighbor is off the board
                continue
            except ValueError:  # Current node is not created yet
                yield neighbor_coords
