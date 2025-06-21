# AGENT.md

Quick reference for coding assistants working in this repository.

## Build/Lint/Test Commands

- **Install dependencies:** `uv sync`
- **Run all tests:** `uv run pytest`
- **Run single test:** `uv run pytest tests/test_translations.py::test_function_name`
- **Lint & format:** `uv run ruff check --fix && uv run ruff format`
- **Run application:** `uv run litellm-ollama-shim` (starts on port 4000)

## Architecture & Structure

- **Main module:** `src/litellm_ollama_shim/` - FastAPI wrapper exposing Ollama-compatible endpoints
- **Core functionality:** Translates between LiteLLM proxy and Ollama API formats
- **Key endpoints:** `/api/tags`, `/api/chat`, `/api/show` - wrap underlying LiteLLM proxy
- **Types:** Pydantic models in `types.py` for request/response schemas
- **Entry point:** `__main__.py` with uvicorn server setup

## Code Style Guidelines

- **Imports:** Use `from __future__ import annotations`, group stdlib/3rd-party/local
- **Types:** Full type hints with Pydantic models for API schemas, use `Any` for dynamic responses
- **Naming:** Snake_case functions/variables, PascalCase classes, descriptive names
- **Error handling:** FastAPI JSONResponse with proper HTTP status codes
- **Formatting:** Ruff with E/F/B/UP/SIM/I/RUF rules enabled, ignore E501 (line length)
- **Dependencies:** Use `uv` exclusively, avoid direct `pip` calls
