# litellm-ollama-shim
A lightweight FastAPI wrapper that exposes three Ollama‑compatible endpoints
(`/api/tags`, `/api/chat`, `/api/show`) on top of the stock LiteLLM proxy.

```bash
# starts the server on port 4000
uvx --from=git+https://github.com/unstableneutron/litellm-ollama-shim \
 litellm-ollama-shim
```
