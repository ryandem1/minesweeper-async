clean:
	docker rm -f minesweeper

build:
	docker build -t minesweeper .

run:
	docker run -d -t --name minesweeper minesweeper

dev:
	docker run -d -t -p 127.0.0.1:8000:8000 -v $(CURDIR)/src:/minesweeper --name minesweeper minesweeper
