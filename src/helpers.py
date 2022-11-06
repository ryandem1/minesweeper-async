from asyncio import sleep
from random import randint
from typing import Coroutine, Any
from uuid import UUID

from fastapi import HTTPException

from models import Board, BoardSpace
from settings import LatencyValue

MILLISECONDS = 0.001


async def wait_for(latency: LatencyValue) -> Coroutine[Any, Any, Any]:
    """
    Sleeps thread for a certain amount of milliseconds or a randomly selected amount of milliseconds from a range.

    Parameters
    ----------
    latency : LatencyValue
        Either a range of 2 ints or a single int value of the # milliseconds to sleep for

    Returns
    -------
    Coroutine
    """
    match latency:
        case int(min_), int(max_) if min_ < max_ and max_ > 0:
            sleep_time = randint(min_, max_)
        case int(value) if value > 0:
            sleep_time = value
        case _:
            raise ValueError(f"Invalid latency value: {latency}")
    return await sleep(sleep_time * MILLISECONDS)


def get_board_by_id_or_error(board_id: UUID, boards: list[Board]) -> Board:
    """
    Retrieves a board by ID from a list or will throw an HTTP exception if it doesn't exist.

    Parameters
    ----------
    board_id : UUID
        ID of the board to retrieve from the list

    boards : list[Board]
        Board list to query

    Returns
    -------
    board : Board
        Board from the list if it exists
    """
    if board := next((b for b in boards if b.id == board_id), None):
        return board

    raise HTTPException(
        status_code=400,
        detail="Board not found!"
    )


def get_space_on_board_or_error(space: BoardSpace, board: Board) -> BoardSpace:
    """
    Retrieves a space on a board by coordinates.

    Parameters
    ----------
    space : BoardSpace
        Coordinates of the space to get.

    board : Board
        Minesweeper board to check

    Returns
    -------
    space : BoardSpace
        space if it exists on the board, or else will raise a `HTTPException`
    """
    try:
        space = board[space]
    except IndexError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    return space
