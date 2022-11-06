from fastapi import FastAPI, HTTPException
import models

app = FastAPI()

SCORE = 0


@app.get("/score")
async def _():
    return models.Score(SCORE)


@app.get("/boards")
async def _(amount: int = 1):
    if not 51 > amount > 0:
        raise HTTPException(status_code=400, detail="Amount must be 51 > amount > 0!")

    boards = [models.Board() for _ in range(amount)]
    return boards


@app.post("/check")
async def _():
    global SCORE
    SCORE += 1
    return models.Score(SCORE)
