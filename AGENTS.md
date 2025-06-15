# AGENTS.md

Quick reference for common development tasks in this repository.

## Dependency Management

- **Install pinned dependencies:**
  ```bash
  uv sync
  ```

- **Add a dependency** (example: Flask):
  ```bash
  uv add flask
  ```

- **Remove a dependency** (example: requests):
  ```bash
  uv remove requests
  ```

## Running Tests

```bash
uvx pytest
```

## Linting and Formatting (auto-fix)

```bash
uvx ruff check --fix && uvx ruff format
```

---

**Rules of thumb**

- Always use **uv** for adding or removing Python packages.
- Avoid calling `pip` directly; it bypasses the lockfile and can cause drift.
- Keep CI green by running tests and lint/format before committing.

