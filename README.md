# minesweeper-async
A game about async processing and imperfect information.

### Parameters
1. All Minesweeper boards in this game will be the standard **9x9** minesweeper boards with 10 mines on each board.
2. Information about boards can be inferred from data provided from the various endpoints in the `minesweeper` server
3. No endpoint will really give full information, and generally, the more informative an endpoint is, the longer the latency will be
4. The `minesweeper` can also check boards for correctness

### The Goal
- Process as many boards as possible, as accurately as possible in 10 minutes

### Scoring
Because of the imperfect nature of all of this, our answers might not be perfect. The idea is that you will have to balance
out accuracy for performance. Here is the score breakdown:

| Action                     | Point Value           | Description                                                                                                             |
|----------------------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------|
| Board Processed            | +5                    | Successfully submitting a value board to `/check`                                                                       |
| Mine Flagged               | +9                    | Each correctly flagged mine on a submitted board                                                                        |
| Safe Space Hit             | +Value of Space       | Each correctly hit safe space on a submitted board will increase score by the # of mines in immediate proximity         |
| Fully Accurate Board Bonus | +20                   | Bonus for submitting a fully accurate board (all mines flagged correctly, all safe spaces hit correctly, no undefineds) |
| Space Undefined            | -2                    | Penalty for not defining if a space is safe or flagged                                                                  |
| Safe Space Flagged         | -(Value of Space + 1) | Penalty for flagging a safe space is # of mines in immediate proximity + 1                                              |
| Mine Hit                   | -10                   | Penalty for hitting a mine                                                                                              |
