from fastapi import FastAPI, HTTPException
import models

app = FastAPI()

SCORE = 0
OUTSTANDING_BOARDS: list[models.Board] = []  # Boards that have been requested but not returned
BOARD_SIZE_LIMIT = 50  # Amount of boards that can be outstanding at once


@app.get("/score")
async def _():
    return models.Score(SCORE)


@app.get("/board")
async def _():
    global OUTSTANDING_BOARDS

    if len(OUTSTANDING_BOARDS) > BOARD_SIZE_LIMIT:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide another board until one is checked in!"
        )

    board = models.Board()
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
