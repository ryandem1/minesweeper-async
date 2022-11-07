"""
Determines whether each space is a mine, marks accordingly, and then submits the board at the end, all synchronously.

Score: 250
"""
import itertools

from requests import Session


def main():
    session = Session()
    base_url = "http://localhost:8000"

    while True:
        response = session.post(base_url + "/board")
        response.raise_for_status()
        response_body = response.json()

        board_id = response_body["id"]
        board_length = response_body["settings"]["length"]
        board_height = response_body["settings"]["height"]

        for x, y in itertools.product(range(board_length), range(board_height)):
            response = session.get(
                base_url + "/is_space_a_mine",
                params={"board_id": board_id},
                json={"x": x, "y": y}
            )
            response.raise_for_status()
            space_is_a_mine = response.json()["answer"]
            if space_is_a_mine:
                session.post(base_url + "/flag", params={"board_id": board_id}, json={"x": x, "y": y})
            else:
                session.post(base_url + "/hit", params={"board_id": board_id}, json={"x": x, "y": y})

        score_response = session.post(base_url + "/check", params={"board_id": board_id})
        score_response.raise_for_status()
        score = score_response.json()["score"]
        print(f"Current score: {score}")


if __name__ == '__main__':
    main()
