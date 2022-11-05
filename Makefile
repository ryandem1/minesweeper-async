clean:
	docker rm -f minesweeper-server

build:
	docker build -t minesweeper-server .

run:
	docker run -d -t --name minesweeper-server minesweeper-server
