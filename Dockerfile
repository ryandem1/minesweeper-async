FROM python:3.11
WORKDIR /minesweeper

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
