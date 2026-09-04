# Fully Local Private Document Assistant
## Gemma 4 + Google ADK + Ollama

A fuller local document-assistant project built to demonstrate several Google ADK concepts in one coherent application:

- Local Gemma 4 inference through Ollama
- ADK function tools
- PDF and mixed-file document access
- Cross-document search and comparison
- Persistent user-scoped preferences with ADK state + SQLite sessions
- Cross-session conversational recall with ADK MemoryService
- Saved Markdown briefs using ADK artifacts
- ADK Web traces for inspecting tool calls

No Gemini API key is required.

## Project structure

```text
adkdocs/
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── document_tools.py
│   ├── personalization_tools.py
│   ├── artifact_tools.py
│   ├── workspace/
│   │   ├── Atlas_Product_Brief_v3.pdf
│   │   ├── June_Customer_Research.pdf
│   │   ├── Launch_Review_Notes_0818.pdf
│   │   └── release-checklist.md
│   └── tests/
│       ├── test_agent.py
│       ├── test_artifact_tools.py
│       └── test_tools.py
├── pyproject.toml
├── requirements.txt
├── run-local.sh
└── run-local.ps1
```

For a compact tutorial structure, the ADK agent files and their tests live
directly under `src/`. The editable install configured by `requirements.txt`
makes the `src` package importable without modifying `sys.path`.

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

PowerShell on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Test the document layer

```bash
python -m unittest discover -s src/tests -v
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
- ADK's in-memory MemoryService for cross-session recall while the server runs
- Ollama at `http://localhost:11434`

The launchers convert the artifact directory to an absolute `file://` URI, as
required by current ADK releases (and especially important on Windows).

Open the local ADK Web URL and select `src`.

ADK Web is launched directly against `src/`, which is the single agent folder.
Its `__init__.py` imports `agent`, and `agent.py` exposes `root_agent`, which
are the discovery conventions ADK uses. For a discovery-only manual launch,
use:

```bash
adk web src
```

Use the provided launcher for the complete demo because it also configures the
persistent SQLite session service and file-backed artifact service.

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

### E. Cross-session conversational memory

In one session:

```text
The Northwind dependency is the issue I am most worried about.
```

Create a new session without stopping the ADK server, then ask:

```text
What did I say I was most worried about earlier?
```

The agent calls ADK's built-in `load_memory` tool. The after-agent callback
adds only user-authored events to MemoryService, preventing model reasoning and
tool traces from polluting recall while preserving the normal ADK memory
workflow shown in the trace.

`memory://` is deliberately zero-config and fully local for this tutorial. It
spans sessions for the same user while the server is running, but its contents
are cleared when the ADK server restarts.

### F. Saved and retrievable artifacts

```text
Review the launch documents, create a concise launch-risk brief with evidence,
and save it.
```

The agent first gathers document evidence and then calls `save_brief`. It can
also save a longer Markdown draft intended for editing before publishing on a
platform such as Medium. To retrieve the content in the same session, ask:

```text
What briefs have I saved?
Open Launch_Risk_Brief.md.
```

The agent uses `list_saved_briefs` and `load_saved_brief`. The result is stored
as a local ADK artifact and can also be inspected through the Artifacts view.
On disk, session-scoped artifacts are stored under:

```text
.adk/artifacts/apps/src/users/<user>/sessions/<session-id>/artifacts/
  <filename>/versions/<version>/
```

The `.adk/` directory is excluded from Git so private sessions and generated
artifacts are not committed.

## What is persistent?

| Feature | Across new session | Across ADK restart |
|---|---|---|
| Conversation history | No | Yes, when reopening its original session |
| `user:` preferences/state | Yes | Yes |
| Pinned document state | Yes | Yes |
| `memory://` conversational memory | Yes | No |
| Session-scoped artifacts | No | Yes, when reopening its original session |

New sessions begin with an empty conversation and their own artifact scope, but
they inherit the same user's saved preferences and pinned-document state.

## Why no vector database?

This version intentionally uses direct reading plus keyword search.

That makes it possible to explain the complete system before introducing
embeddings or semantic retrieval. Local RAG is a natural follow-up project once
the document collection grows.

## Privacy boundary

Source-document tools are read-only and restricted to:

`src/workspace/`

The local model is served by Ollama. The project does not require a cloud LLM API key.
