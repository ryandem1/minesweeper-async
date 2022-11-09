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
async def _() -> models.Score:
    """
    Returns the current score.

    Returns
    -------
    score : models.Score
        Current score like: {"score": <score_int>}
    """
    return models.Score(SCORE)


@app.post("/board")
async def _() -> models.Board:
    """
    Generates a new board if there is space available for another outstanding board. Will return the ID of the created
    board.

    Returns
    -------
    board : dict[str, UUID]
        Response format like: {"id": "<new_board_uuid>"}
    """
    global OUTSTANDING_BOARDS

    if len(OUTSTANDING_BOARDS) > settings.app.max_boards:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide another board until one is checked in!"
        )

    board = models.Board.new(settings=settings.board)
    OUTSTANDING_BOARDS.append(board)

    await helpers.wait_for(settings.latency.board)
    return models.Board(id=board.id, settings=board.settings)


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
    space.flagged = False

    await helpers.wait_for(settings.latency.hit)
    return space


@app.post("/batch_hit")
async def _(board_id: UUID, spaces: list[models.BoardSpace]) -> list[models.BoardSpace]:
    """
    Hit spaces on the board. The spaces must all be neighbors. For this endpoint, if any of the spaces are mines, it
    will return a 400 error and the spaces will not be hit

    Parameters
    ----------
    board_id : UUID
        ID of the board to hit the space on

    spaces : list[models.BoardSpace]
        Coordinates of spaces to hit

    Returns
    -------
    revealed_spaces : list[models.BoardSpace]
        Spaces that were hit
    """
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)
    spaces = [helpers.get_space_on_board_or_error(space, board) for space in spaces]
    if any(space for space in spaces if space.type == models.BoardSpaceType.MINE):
        raise HTTPException(
            status_code=400,
            detail="Batch hits cannot include mines!"
        )
    for space in spaces:
        if space.hit:
            raise HTTPException(
                status_code=400,
                detail="A space in the batch was already hit!"
            )
        space.hit = True
        space.flagged = False

    await helpers.wait_for(settings.latency.batch_hit)
    return spaces


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
    if len([space for space in board if space.flagged]) >= board.settings.mines:
        raise HTTPException(
            status_code=400,
            detail="Cannot place another flag! Flags are limited to the # of mines on a board"
        )
    space.flagged = not space.flagged

    await helpers.wait_for(settings.latency.flag)
    return models.BoardSpace(
        x=space.x,
        y=space.y,
        flagged=space.flagged
    )


@app.post("/check")
async def _(board_id: UUID) -> models.Score:
    """
    Checks a board for correctness, assigns points, and frees up the space in `OUTSTANDING_BOARDS`

    Parameters
    ----------
    board_id : UUID
        ID of the board to check

    Returns
    -------
    score : models.Score
        Current score after checking
    """
    global SCORE
    global OUTSTANDING_BOARDS

    board_score = 0
    board = helpers.get_board_by_id_or_error(board_id, OUTSTANDING_BOARDS)

    # Flat Processing bonus equal to length and height of the board
    board_score += board.settings.length + board.settings.height

    # Add up all safe, value spaces that were hit
    board_score += sum(
        space.value
        for space in board
        if space.type == models.BoardSpaceType.VALUE and space.hit
    )

    # Penalty for accuracy
    number_of_mines_flagged = len([
        space
        for space in board
        if space.type == models.BoardSpaceType.MINE and space.flagged
    ])
    accuracy = number_of_mines_flagged / board.settings.mines
    board_score *= accuracy

    SCORE += board_score
    OUTSTANDING_BOARDS.remove(board)

    await helpers.wait_for(settings.latency.check)
    return models.Score(SCORE)
