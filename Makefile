HOST = 127.0.0.1
PORT = 8000


.PHONY: start
start:
	uv run uvicorn app.main:app --reload --host $(HOST) --port $(PORT)