from uuid import UUID

from fastapi import FastAPI, HTTPException

import helpers
import models
from settings import Settings

app = FastAPI()
settings = Settings()

SCORE = 0
OUTSTANDING_BOARDS: list[models.Board] = []  # Boards that have been requested but not returned


@app.get("/score")
async def _():
    return models.Score(SCORE)


@app.post("/board")
async def _():
    global OUTSTANDING_BOARDS

    if len(OUTSTANDING_BOARDS) > settings.app.max_boards:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide another board until one is checked in!"
        )

    board = models.Board.new(settings=settings.board)
    OUTSTANDING_BOARDS.append(board)

    await helpers.wait_for(settings.latency.board)
    return {"id": board.id}


@app.post("/hit")
async def _(board_id: UUID, space: models.BoardSpace) -> models.BoardSpace:
    """
    Hits a space on a board by ID and space coordinates. Will return the actual space.

    Parameters
    ----------
    board_id : UUID
        ID of the board to hit the space on

    space : models.BoardSpace
        Coordinates of space to hit

    Returns
    -------
    revealed_space : models.BoardSpace
        Space that was hit
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    space = helpers.get_space_on_board_or_error(space, board)

    if space.hit:
        raise HTTPException(
            status_code=400,
            detail="Space already hit!"
        )
    space.hit = True

    await helpers.wait_for(settings.latency.hit)
    return space


@app.post("/flag")
async def _(board_id: UUID, space: models.BoardSpace) -> models.BoardSpace:
    """
    Toggles a flag on a space on a board by ID and space coordinates.

    Parameters
    ----------
    board_id : UUID
        ID of the board that the space is on

    space : models.BoardSpace
        Coordinates of the space to flag

    Returns
    -------
    space : models.BoardSpace
        Coordinates and flag status of space
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    space = helpers.get_space_on_board_or_error(space, board)

    if space.hit:
        raise HTTPException(
            status_code=400,
            detail="Cannot flag space, it has already been hit!"
        )
    space.flagged = not space.flagged

    await helpers.wait_for(settings.latency.flag)
    return models.BoardSpace(
        x=space.x,
        y=space.y,
        flagged=space.flagged
    )


@app.post("/check")
async def _(board: models.Board):
    global SCORE
    global OUTSTANDING_BOARDS

    correct_board = helpers.get_board_by_id_or_error(board.id, OUTSTANDING_BOARDS)

    OUTSTANDING_BOARDS.remove(correct_board)

    await helpers.wait_for(settings.latency.check)
    return models.Score(SCORE)


@app.get("/is_space_blank")
async def _(board_id: UUID, space: models.BoardSpace) -> models.Answer:
    """
    Checks if space is blank, pretty cheap option. Costs 200-300 ms

    Parameters
    ----------
    board_id : UUID
        ID of the board that the space is on

    space : models.BoardSpace
        Coordinates of the space to flag

    Returns
    -------
    response : dict[str, bool]
        Format: {"answer": <bool>}
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    space_type = helpers.get_space_on_board_or_error(space, board).type

    await helpers.wait_for(settings.latency.is_space_blank)
    return models.Answer(space_type == models.BoardSpaceType.BLANK)


@app.get("/get_space_value")
async def _(board_id: UUID, space: models.BoardSpace) -> models.Answer:
    """
    Gets the amount of mines immediate adjacent to the space by coordinates. Note that mines also have a value, and they
    count themselves, so they will not necessarily be detectable from determining their value.

    Parameters
    ----------
    board_id : UUID
        ID of the board that the space is on

    space : models.BoardSpace
        Coordinates of the space to flag

    Returns
    -------
    answer : models.Answer
        Format: {"answer": <int_value>}
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    space = helpers.get_space_on_board_or_error(space, board)

    await helpers.wait_for(settings.latency.get_space_value)
    return models.Answer(space.value)
