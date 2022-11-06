from fastapi import FastAPI, HTTPException
from settings import Settings
import models


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
    return board


@app.post("/check")
async def _(board: models.Board):
    global SCORE
    global OUTSTANDING_BOARDS

    correct_board = next((b for b in OUTSTANDING_BOARDS if b.id == board.id), None)
    if not correct_board:
        raise HTTPException(
            status_code=400,
            detail="Board not found!"
        )

    OUTSTANDING_BOARDS.remove(correct_board)
    return models.Score(SCORE)
