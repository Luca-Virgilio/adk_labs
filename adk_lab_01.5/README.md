## PRE-REQUISITES
- uv
- python 3.11

## FIRST CREATION
```bash
uv venv
source .venv/bin/activate
uv init
uv add google-adk
uv pip install -r requirements.txt
uv pip install "google-adk[extensions]"
```
## INSTALLATION
```bash
uv sync
```

## RUNNING
```bash
uv run adk web
```

## TESTING
```bash

```
