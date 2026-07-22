SHELL := /bin/bash

VENV    := backend/.venv
UVICORN := $(VENV)/bin/uvicorn
PYTEST  := $(VENV)/bin/pytest

.PHONY: install dev be fe test-be test-fe

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

test-be:
	@test -f $(PYTEST) || { echo "Error: $(PYTEST) not found — run 'make install' first."; exit 1; }
	$(PYTEST) backend/tests -v

test-fe:
	cd frontend && npm run test

.PHONY: finish-task
finish-task:
	@if [ -z "$(id)" ]; then \
		echo "Error: task id required — run 'make finish-task id=010'"; exit 1; \
	fi
	@TASK_FILE=$$(ls docks/dev/IN_PROGRESS/$(id)-*.md 2>/dev/null | head -n1); \
	if [ -z "$$TASK_FILE" ]; then \
		echo "Error: no file matching docks/dev/IN_PROGRESS/$(id)-*.md"; exit 1; \
	fi; \
	TASK_BASENAME=$$(basename "$$TASK_FILE"); \
	CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$CURRENT_BRANCH" != "main" ]; then \
		git switch main; \
	fi; \
	git pull; \
	git switch -c finish-$(id); \
	mv "$$TASK_FILE" "docks/dev/DONE/$$TASK_BASENAME"; \
	git add -A; \
	git commit -m "finish $$TASK_BASENAME"; \
	git push -u origin finish-$(id); \
	gh pr create \
		--title "finish $$TASK_BASENAME" \
		--body "Moves $$TASK_BASENAME from IN_PROGRESS to DONE." \
		--base main
