from uuid import UUID
from models import Board
from fastapi import HTTPException


MILLISECONDS = 0.001


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
