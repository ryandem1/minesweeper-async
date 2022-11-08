import itertools
import random

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
        board_mines = response_body["settings"]["mines"]
        board_height = response_body["settings"]["height"]

        available_coordinates = list(itertools.product(range(board_length), range(board_height)))
        flag_spots = [
            available_coordinates.pop(random.randint(0, len(available_coordinates) - 1))
            for _ in range(board_mines)
        ]
        for x, y in available_coordinates:
            session.post(base_url + "/hit", params={"board_id": board_id}, json={"x": x, "y": y})

        for x, y in flag_spots:
            session.post(base_url + "/flag", params={"board_id": board_id}, json={"x": x, "y": y})

        score_response = session.post(base_url + "/check", params={"board_id": board_id})
        score_response.raise_for_status()
        print(f"Current score: {score_response.json()['score']}")


if __name__ == '__main__':
    main()
