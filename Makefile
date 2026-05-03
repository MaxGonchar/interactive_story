SHELL := /bin/bash

VENV    := backend/.venv
UVICORN := $(VENV)/bin/uvicorn

.PHONY: install dev be fe

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

dev:
	@BE_PID=; FE_PID=; \
	trap 'kill $$BE_PID $$FE_PID 2>/dev/null; exit 1' SIGINT SIGTERM; \
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend & BE_PID=$$!; \
	cd frontend && npm run dev & FE_PID=$$!; \
	wait $$BE_PID; BE_EXIT=$$?; \
	kill $$FE_PID 2>/dev/null; \
	exit $$BE_EXIT

be:
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend

fe:
	cd frontend && npm run dev
