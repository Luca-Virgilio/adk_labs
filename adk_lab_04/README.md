## Install
1. Install packages

```sh
uv sync
```

```sh
uv pip install -r requirements.txt
```

2. Create or upadte .env file in agents folder

```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=key
MODEL=gemini-2.5-flash
```

## Run
```sh
uv run python3 adk_mcp_server/adk_mcp_server.py

```

```sh
uv run adk web

```