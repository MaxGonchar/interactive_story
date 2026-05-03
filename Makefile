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
	@trap 'kill 0' SIGINT SIGTERM; \
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend & \
	cd frontend && npm run dev & \
	wait

be:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

fe:
	cd frontend && npm run dev
