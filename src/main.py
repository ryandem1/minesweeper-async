import asyncio
from random import randint
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


@app.get("/board")
async def _():
    global OUTSTANDING_BOARDS

    if len(OUTSTANDING_BOARDS) > settings.app.max_boards:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide another board until one is checked in!"
        )

    board = models.Board.new(settings=settings.board)
    OUTSTANDING_BOARDS.append(board)
    return {"id": board.id}


@app.get("/is_space_blank")
async def _(board_id: UUID, space: models.BoardSpace) -> models.Answer:
    """
    Checks if space is blank, pretty cheap option. Costs 200-300 ms

    Parameters
    ----------
    space : models.BoardSpace
        Space to check

    Returns
    -------
    response : dict[str, bool]
        Format: {"answer": <bool>}
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    try:
        space_type = board[space].type
    except IndexError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    await asyncio.sleep(randint(200, 300) * helpers.MILLISECONDS)
    return models.Answer(True) if space_type == models.BoardSpaceType.BLANK else models.Answer(False)


@app.post("/check")
async def _(board: models.Board):
    global SCORE
    global OUTSTANDING_BOARDS

    correct_board = helpers.get_board_by_id_or_error(board.id, OUTSTANDING_BOARDS)

    OUTSTANDING_BOARDS.remove(correct_board)
    return models.Score(SCORE)
