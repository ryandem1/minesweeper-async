# minesweeper-async
A game about async processing, imperfect information, and trading accuracy for performance.

If you are unfamiliar with the Windows "Minesweeper game", here is the Wikipedia with the rundown: \
[Minesweeper Game Wikipedia](https://en.wikipedia.org/wiki/Minesweeper_(video_game))

While the game is functionally the same, there are a few differences with Async Minesweeper, specifically with the goal
of the game and a few of the rules.

1. Instead of completing 1 board, this game is more about processing many Minesweeper boards as quickly as possible, while remaining as accurate as possible
2. Hitting a mine on a board does not end the board
3. There is a scoring system that assigns points based on accuracy, scores can be negative, see chart below
4. The idea is that, to get a high score, one must balance performance and accuracy
5. While in normal Minesweeper, there can be circumstances where, given perfect analysis of all available information, 
it is impossible to determine with 100% that a space is or is not a mine without guessing; in Async Minesweeper, you 
can ask the server questions about the board at the cost of latency depending on how informative the question is. This
way, it is possible to accurately determine every space of every board


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
3. Information about boards can be inferred from data provided from the various discovery endpoints in the `minesweeper` server.
4. Data gathering endpoints are formatted like questions to the server.
5. No endpoint will really give full information, and generally, the more informative an endpoint is, the longer the latency will be
6. Boards will only be counted when they are checked by passing the ``board_id`` to `/check`
7. Boards do not have to be completely hit/flagged to be submitted, but any untouched mines will be deducted like they were hit, and you will miss out on any non-hit Value spaces.

### The Goal
- Process as many boards as possible, as accurately as possible in 10 minutes

### Scoring
Because of the imperfect nature of all of this, our answers might not be perfect. The idea is that you will have to balance
out accuracy for performance. Here is the score breakdown:

| Action                     | Point Value                            | Description                                                                                                             |
|----------------------------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Board Processed            | +(Board Length + Board Height)         | Successfully submitted a valid board to `/check`                                                                        |
| Fully Accurate Board Bonus | x1.25                                  | Bonus for submitting a fully accurate board (all mines flagged correctly, all safe spaces hit correctly, no undefineds) |
| Safe Space Hit             | +Value of Space                        | Each correctly hit safe space on a submitted board will increase score by the # of mines in immediate proximity         |
| Safe Space Flagged         | -Value of Space                        | Penalty for flagging a safe space is # of mines in immediate proximity                                                  |
| Mine Flagged               | +(Sum of all neighboring space values) | Each correctly flagged mine on a submitted board                                                                        |
| Mine Hit                   | -(Sum of all neighboring space values) | Penalty for hitting a mine                                                                                              |
| Mine Missed                | -(Sum of all neighboring space values) | Penalty for submitting a board with an un-flagged mine                                                                  |

### Action Endpoints

Action endpoints can create/interact/check a minesweeper board.

| Endpoint | Method | Description                                                                                                                                                            | Query Parameter(s)                                              | Sample Request Body |
|----------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|---------------------|
| `/board` | `POST` | Creates a new Minesweeper board internally and will return the caller the UUID                                                                                         | N/A                                                             | N/A                 |
| `/hit`   | `POST` | Hits a Minesweeper space by board/coordinates, like if you clicked the space on Windows. Throws an error if the space has been hit already. Returns the revealed space | `board_id : UUID`: ID of an existing Minesweeper board to query | `{"x": 0, "y": 0}`  |
| `/flag`  | `POST` | Toggles flag on a Minesweeper board space. Throws an error if the space has been hit already. Returns the flag status of space                                         | `board_id : UUID`: ID of an existing Minesweeper board to query | `{"x": 0, "y": 0}`  |
| `/check` | `POST` | Will check the provided board, update the score, and free up a space in the overall outstanding boards.                                                                | N/A                                                             | TBD                 |

### Discovery Endpoints

Discovery endpoints can provide information about the spaces on a board without interacting with them. Because these
endpoint can be pretty informative, they typically have a high latency to use.

| Endpoint           | Method | Description                                                                                                                                                                                                     | Query Parameter(s)                                              | Sample Request Body |
|--------------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|---------------------|
| `/is_space_blank`  | `GET`  | Returns a bool answer whether or not the space is a free space (no value/no mine)                                                                                                                               | `board_id : UUID`: ID of an existing Minesweeper board to query | `{"x": 0, "y": 0}`  |
| `/get_space_value` | `GET`  | Gets the amount of mines immediate adjacent to the space by coordinates. Note that mines also have a value, and they count themselves, so they will not necessarily be detectable from determining their value. | `board_id : UUID`: ID of an existing Minesweeper board to query | `{"x": 0, "y": 0}`  |
| `/is_space_a_mine` | `GET`  | Returns if the space on the given board is a mine. Because this is valuable information, this endpoint has a 50% chance of returning a 503 error instead of answering.                                          | `board_id : UUID`: ID of an existing Minesweeper board to query | `{"x": 0, "y": 0}`  |
