from fastapi import FastAPI
import models

app = FastAPI()

SCORE = 0


@app.get("/score")
async def _():
    return models.Score(SCORE)


@app.post("/check")
async def _():
    global SCORE
    SCORE += 1
    return models.Score(SCORE)
