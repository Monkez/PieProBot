.PHONY: install dev backend frontend test lint

install:
	.venv/Scripts/pip.exe install -e .[test]
	cd frontend && npm install

dev:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

backend:
	cd backend && ../.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev -- -p 3000

test:
	cd backend && ../.venv/Scripts/python.exe -m pytest

lint:
	cd backend && ../.venv/Scripts/python.exe -m compileall app
