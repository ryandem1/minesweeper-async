# minesweeper-async
A game about async processing, imperfect information, and trading accuracy for performance.

If you are unfamiliar with the Windows "Minesweeper game", here is the Wikipedia with the rundown: \
[Minesweeper Game Wikipedia](https://en.wikipedia.org/wiki/Minesweeper_(video_game))

While the game is functionally the same, there are a few differences with Async Minesweeper, specifically with the goal
of the game and a few of the rules.

1. Instead of completing 1 board, this game is more about processing many Minesweeper boards as quickly as possible, while remaining as accurate as possible
2. Hitting a mine on a board does not end the board
3. There is a scoring system that assigns points based on accuracy, see chart below
4. The idea is that, to get a high score, one must balance performance and accuracy


Here is a note on the computation complexity of Minesweeper that I stole from Wikipedia:

"""\
In 2000, Richard Kaye published a proof that it is NP-complete to determine whether a given grid of uncovered, correctly 
flagged, and unknown squares, the labels of the foremost also given, has an arrangement of mines for which it is possible 
within the rules of the game. The argument is constructive, a method to quickly convert any Boolean circuit into such a 
grid that is possible if and only if the circuit is satisfiable; membership in NP is established by using the arrangement 
of mines as a certificate. If, however, a minesweeper board is already guaranteed to be consistent, solving it is not 
known to be NP-complete, but it has been proven to be co-NP-complete. In the latter case, however, minesweeper exhibits 
a phase transition analogous to k-SAT: when more than 25% squares are mined, solving a board requires guessing an 
exponentially-unlikely set of mines. Kaye also proved that infinite Minesweeper is Turing-complete.\
"""

### Parameters
1. Minesweeper board size/mine count is configurable, the default is the standard 9x9, 10 mine boards from Windows.
2. All endpoint latency values are configurable via environment vars
3. Data gathering endpoints are formatted like questions to the server.
4. No endpoint will really give full information, and generally, the more informative an endpoint is, the longer the latency will be
5. Boards will only be counted when they are checked by passing the ``board_id`` to `/check`
6. Boards do not have to be completely hit/flagged to be submitted, but any untouched mines will be deducted like they were hit, and you will miss out on any non-hit Value spaces.

### The Goal
- Process as many boards as possible, as accurately as possible within a limited timeframe.

### Scoring
Because of the imperfect nature of all of this, our answers might not be perfect. The idea is that you will have to balance
out accuracy for performance. The goal of this scoring is to be scalable to various board sizes. Here is the score breakdown:

| Item               | Point Value                                                             | Description                                                                                                     |
|--------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Board Processed    | +(Board Length + Board Height)                                          | Successfully submitted a valid board to `/check`                                                                |
| Safe Space Hit     | +Value of Space                                                         | Each correctly hit safe space on a submitted board will increase score by the # of mines in immediate proximity |
| Mine Accuracy      | Entire score gets multiplied by (number of mines flagged / total mines) | Each correctly flagged mine on a submitted board.                                                               |

With this scoring, if no mine is flagged correctly, the score for the entire board will be 0. If a board is perfectly accurate,
the score will be equal to the total value of all value spaces on the board + the perimeter of the board.

### Action Endpoints

Action endpoints can create/interact/check a minesweeper board.

| Endpoint     | Method | Description                                                                                                                                                             | Query Parameter(s)                                                            | Sample Request Body |
|--------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------|
| `/board`     | `POST` | Creates a new Minesweeper board internally and will return the caller the UUID                                                                                          | N/A                                                                           | N/A                 |
| `/hit`       | `POST` | Hits a Minesweeper space by board/coordinates, like if you clicked the space on Windows. Throws an error if the space has been hit already. Returns the revealed space  | `board_id : UUID`: ID of the existing Minesweeper board to hit the space on.  | `{"x": 0, "y": 0}`  |
| `/batch_hit` | `POST` | Hit spaces on the board. The spaces must all be neighbors. For this endpoint, if any of the spaces are mines, it will return a 400 error and the spaces will not be hit | `board_id : UUID`: ID of the existing Minesweeper board to hit the space on.  | `{"x": 0, "y": 0}`  |
| `/flag`      | `POST` | Toggles flag on a Minesweeper board space. Throws an error if the space has been hit already. Returns the flag status of space                                          | `board_id : UUID`: ID of the existing Minesweeper board to flag the space on. | `{"x": 0, "y": 0}`  |
| `/check`     | `POST` | Will check the provided board, update the score, and free up a space in the overall outstanding boards.                                                                 | `board_id : UUID`: ID of an existing Minesweeper board to check               | N/A                 |
