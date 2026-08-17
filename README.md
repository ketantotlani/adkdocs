# Fully Local Private Document Assistant
## Gemma 4 + Google ADK + Ollama

A fuller local document-assistant project built to demonstrate several Google ADK concepts in one coherent application:

- Local Gemma 4 inference through Ollama
- ADK function tools
- PDF and mixed-file document access
- Cross-document search and comparison
- Persistent user-scoped preferences with ADK state + SQLite sessions
- Cross-session ADK MemoryService recall
- Saved Markdown briefs using ADK artifacts
- ADK Web traces for inspecting tool calls

No Gemini API key is required.

## Project structure

```text
gemma-adk-private-docs-full/
├── local_doc_agent/
│   ├── agent.py
│   ├── document_tools.py
│   ├── personalization_tools.py
│   ├── artifact_tools.py
│   └── workspace/
│       ├── Atlas_Product_Brief_v3.pdf
│       ├── June_Customer_Research.pdf
│       ├── Launch_Review_Notes_0818.pdf
│       └── release-checklist.md
├── tests/
├── run-local.sh
├── run-local.ps1
├── PUBLICATION_SECTIONS.md
└── requirements.txt
```

## 1. Install and test Gemma 4

```bash
ollama pull gemma4:e2b-it-qat
ollama run gemma4:e2b-it-qat "Reply with exactly: local model works"
```

## 2. Python setup

Git Bash on Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Test the document layer

```bash
python -m unittest discover -s tests -v
```

## 4. Start the full local app

Git Bash:

```bash
bash run-local.sh
```

PowerShell:

```powershell
.\run-local.ps1
```

The launch command configures:

- SQLite-backed ADK sessions at `.adk/sessions.db`
- local file-backed ADK artifacts under `.adk/artifacts`
- ADK's in-memory MemoryService for cross-session recall while the server is running
- Ollama at `http://localhost:11434`

Open the local ADK Web URL and select `local_doc_agent`.

## Demo path

### A. Document tools

```text
What files are available?
```

```text
What is the target release date in the product brief?
```

### B. Cross-document reasoning

```text
What is the current pilot launch date?
Flag any document that still shows an older date and explain what changed.
```

```text
Which customer requests are not included in the first release?
```

```text
Review the product brief, customer research, launch notes, and checklist.
What are the three biggest launch risks, and what evidence supports each one?
```

### C. Persistent user preferences

```text
Remember that I care most about launch blockers and customer feedback.
```

Create a new ADK session, then ask:

```text
What should I focus on when reviewing these documents?
```

The preference is stored as user-scoped ADK state. Because sessions use SQLite,
the user-scoped state can survive new sessions and application restarts.

### D. Pin an important document

```text
Pin Launch_Review_Notes_0818.pdf as important.
```

Then in another session:

```text
Which documents have I marked as important?
```

### E. Cross-session memory

In one session:

```text
The Northwind dependency is the issue I am most worried about.
```

Create a new session without stopping the ADK server:

```text
What did I say I was most worried about earlier?
```

The agent can call ADK's `load_memory` tool. The project automatically adds
session events to the configured MemoryService after agent runs.

`memory://` is intentionally used for the tutorial because it is zero-config
and fully local. It spans sessions while the ADK process is running, but the
MemoryService itself is cleared when the server restarts.

### F. Saved artifacts

```text
Review the launch documents, create a concise launch-risk brief with evidence,
and save it.
```

The agent first gathers document evidence and then calls `save_brief`. The
result is stored as a local ADK artifact and can be inspected through the
Artifacts view.

## What is persistent?

| Feature | Across new session | Across ADK restart |
|---|---|---|
| Current chat history | No | No |
| SQLite session history | Yes | Yes |
| `user:` preferences/state | Yes | Yes |
| Pinned document state | Yes | Yes |
| `memory://` MemoryService | Yes | No |
| File-backed artifacts | Yes* | Yes |

`*` Artifact scope depends on the artifact filename and current session/user.

## Why no vector database?

This version intentionally uses direct reading plus keyword search.

That makes it possible to explain the complete system before introducing
embeddings or semantic retrieval. Local RAG is a natural follow-up project once
the document collection grows.

## Privacy boundary

Source-document tools are read-only and restricted to:

`local_doc_agent/workspace/`

The local model is served by Ollama. The project does not require a cloud LLM API key.
# adkdocs
