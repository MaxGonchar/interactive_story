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
	@test -f $(UVICORN) || { echo "Error: $(UVICORN) not found — run 'make install' first."; exit 1; }
	@set -m; \
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend & BE_PID=$$!; \
	(cd frontend && npm run dev) & FE_PID=$$!; \
	cleanup() { kill -- -$$BE_PID -$$FE_PID 2>/dev/null; wait $$BE_PID $$FE_PID 2>/dev/null; }; \
	trap 'cleanup; exit 130' INT; \
	trap 'cleanup; exit 143' TERM; \
	while kill -0 $$BE_PID 2>/dev/null && kill -0 $$FE_PID 2>/dev/null; do sleep 0.5; done; \
	wait $$BE_PID 2>/dev/null; BE_EXIT=$$?; \
	wait $$FE_PID 2>/dev/null; FE_EXIT=$$?; \
	cleanup; \
	[ $$BE_EXIT -ne 0 ] && exit $$BE_EXIT || exit $$FE_EXIT

be:
	@test -f $(UVICORN) || { echo "Error: $(UVICORN) not found — run 'make install' first."; exit 1; }
	$(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend

fe:
	cd frontend && npm run dev
