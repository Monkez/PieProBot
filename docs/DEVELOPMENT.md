# Development

## Test

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
```

## Frontend Build

```powershell
cd frontend
npm run build
npm audit --audit-level=moderate
```

## Package Install

```powershell
uv pip install --python .\.venv\Scripts\python.exe -e ".[test]"
```

## Change Checklist

For every code change:

1. Update tests or explain why tests are not needed.
2. Update docs if behavior/config/install/architecture/security/memory changes.
3. Run backend tests.
4. Run frontend build if frontend or shared install changes.
5. Run `npm audit --audit-level=moderate` if frontend dependencies change.

## Naming

The canonical bot/product name is **PiePro**. Do not introduce new user-facing names unless explicitly approved.

