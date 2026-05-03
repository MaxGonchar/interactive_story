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
	@test -f $(UVICORN) || { echo "Error: backend venv not found. Run 'make install' first."; exit 1; }
	@$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend & BE_PID=$$!; \
	(cd frontend && npm run dev) & FE_PID=$$!; \
	cleanup() { kill $$BE_PID $$FE_PID 2>/dev/null; wait $$BE_PID $$FE_PID 2>/dev/null; }; \
	trap cleanup INT TERM; \
	wait -n $$BE_PID $$FE_PID; FIRST_EXIT=$$?; \
	cleanup; \
	exit $$FIRST_EXIT

be:
	@test -f $(UVICORN) || { echo "Error: backend venv not found. Run 'make install' first."; exit 1; }
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend

fe:
	cd frontend && npm run dev
