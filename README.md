# litellm-ollama-shim
A lightweight FastAPI wrapper that exposes three Ollama‑compatible endpoints
(`/api/tags`, `/api/chat`, `/api/show`) on top of the stock LiteLLM proxy.

```bash
uv pip install litellm-ollama-shim
uvx litellm-ollama-shim  # starts a proxy on port 4000
```
