# Publication build map

The project is intentionally layered so the article can be published section by section.

## Section 1 — Run Gemma 4 locally
Goal: prove the model works through Ollama.

## Section 2 — Connect Gemma 4 to Google ADK
Goal: start ADK Web and send a normal message through the local model.

## Section 3 — Give the agent document tools
Goal: list, read, search, and inspect PDFs and local files.

## Section 4 — Ask questions across multiple documents
Goal: reconcile dates, scope changes, customer requests, and launch risks.

## Section 5 — Add persistent user preferences
Goal: store user-scoped state such as answer style or focus using ADK state plus SQLite sessions.

Suggested demo:
"Remember that I care most about launch blockers and customer feedback."

Start a new session and ask:
"What should I pay attention to in these documents?"

## Section 6 — Add cross-session ADK memory
Goal: use ADK's MemoryService and `load_memory` tool.

Suggested demo:
Session A: "The biggest thing I want to watch is the Northwind dependency."
Create a new session while the ADK server is still running.
Session B: "What did I say I wanted to watch?"

Important: `memory://` is an in-memory MemoryService, so it spans sessions while the server process is running but is not durable across a restart.

## Section 7 — Save a generated brief as an ADK artifact
Goal: demonstrate artifacts instead of only chat output.

Suggested prompt:
"Review the launch documents, create a short launch-risk brief, and save it."

The saved Markdown artifact should appear in ADK's Artifacts view.

## Section 8 — What this version deliberately does not do
No vector database and no semantic RAG yet. That becomes a natural follow-up article.
