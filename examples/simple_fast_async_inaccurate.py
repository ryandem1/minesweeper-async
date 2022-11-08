"""
Same as the sync inaccurate strategy, but performs it on 5 different boards at once
"""
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests import Session


def main():
    session = Session()
    base_url = "http://localhost:8000"

    response = session.post(base_url + "/board")
    response.raise_for_status()
    response_body = response.json()

    board_id = response_body["id"]
    board_height = response_body["settings"]["height"]
    board_length = response_body["settings"]["length"]

    hit = False
    for x, y in itertools.product(range(board_length), range(board_height)):
        if hit:
            session.post(base_url + "/hit", params={"board_id": board_id}, json={"x": x, "y": y})
        else:
            session.post(base_url + "/flag", params={"board_id": board_id}, json={"x": x, "y": y})
        hit = not hit

    score_response = session.post(base_url + "/check", params={"board_id": board_id})
    score_response.raise_for_status()
    score = score_response.json()["score"]
    return score


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:
        while True:
            futures = [pool.submit(main) for _ in range(5)]
            print(f"Current score: {max([future.result() for future in as_completed(futures)])}")
