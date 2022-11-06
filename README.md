# minesweeper-async
A game about async processing and imperfect information.

### Parameters
1. All Minesweeper boards in this game will be the standard **9x9** minesweeper boards with 10 mines on each board.
2. Information about boards can be inferred from data provided from the various discovery endpoints in the `minesweeper` server.
3. Data gathering endpoints are formatted like questions to the server.
4. No endpoint will really give full information, and generally, the more informative an endpoint is, the longer the latency will be
5. Boards will only be counted when they are checked by passing the ``board_id`` to `/check`
6. Boards do not have to be completely hit/flagged to be submitted, but any remaining un-hit/flagged spaces will be deducted.

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
