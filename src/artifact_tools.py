import re
from typing import Any

import google.genai.types as types
from google.adk.tools import ToolContext


def _safe_filename(title: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", (title or "").strip())
    cleaned = cleaned.strip("._")
    return (cleaned or "document_brief")[:60]


def _infer_sources(content: str) -> list[str]:
    """
    Best-effort fallback when a local model forgets to populate `sources`.
    Finds filenames mentioned in the generated brief.
    """
    if not content:
        return []

    pattern = r'\b[\w .()_-]+\.(?:pdf|docx|md|txt|csv|json|py|yaml|yml)\b'
    matches = re.findall(pattern, content, flags=re.IGNORECASE)

    seen = set()
    sources = []
    for item in matches:
        cleaned = item.strip(" .,-")
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            sources.append(cleaned)

    return sources[:20]


async def save_brief(
    content: str,
    tool_context: ToolContext,
    title: str = "Document Brief",
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """
    Save a generated Markdown brief as an ADK artifact.

    Only `content` is required. `title` and `sources` are optional on purpose:
    smaller local models sometimes omit optional-looking structured arguments
    during tool calling. If sources are omitted, filenames are inferred from
    the brief when possible.
    """
    content = (content or "").strip()
    title = (title or "Document Brief").strip()

    if not content:
        return {
            "status": "error",
            "message": "Brief content cannot be empty.",
        }

    normalized_sources = [
        str(source).strip()
        for source in (sources or [])
        if str(source).strip()
    ]

    if not normalized_sources:
        normalized_sources = _infer_sources(content)

    source_lines = "\n".join(
        f"- {source}" for source in normalized_sources
    ) or "- Sources were not explicitly supplied."

    markdown = (
        f"# {title}\n\n"
        f"{content}\n\n"
        "## Sources\n"
        f"{source_lines}\n"
    )

    filename = f"{_safe_filename(title)}.md"

    artifact = types.Part.from_bytes(
        data=markdown.encode("utf-8"),
        mime_type="text/markdown",
    )

    try:
        version = await tool_context.save_artifact(
            filename=filename,
            artifact=artifact,
        )
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Could not save artifact: {exc}",
        }

    return {
        "status": "success",
        "filename": filename,
        "version": version,
        "sources": normalized_sources,
    }


async def list_saved_briefs(tool_context: ToolContext) -> dict[str, Any]:
    """List briefs and other artifacts saved for the current session/user."""
    try:
        artifacts = await tool_context.list_artifacts()
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Could not list artifacts: {exc}",
        }

    return {
        "status": "success",
        "artifacts": artifacts,
    }


async def load_saved_brief(
    filename: str,
    tool_context: ToolContext,
    version: int | None = None,
) -> dict[str, Any]:
    """Load a saved Markdown brief from the current ADK session."""
    filename = (filename or "").strip()

    if (
        not filename
        or "/" in filename
        or "\\" in filename
        or filename in {".", ".."}
    ):
        return {
            "status": "error",
            "message": "Provide a saved artifact filename such as Launch_Brief.md.",
        }

    try:
        artifact = await tool_context.load_artifact(
            filename=filename,
            version=version,
        )
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Could not load artifact: {exc}",
        }

    if artifact is None:
        return {
            "status": "error",
            "message": f"Artifact not found: {filename}",
        }

    inline_data = artifact.inline_data
    if inline_data is None or inline_data.data is None:
        return {
            "status": "error",
            "message": f"Artifact has no readable inline content: {filename}",
        }

    try:
        content = inline_data.data.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": f"Artifact is not UTF-8 text: {filename}",
        }

    return {
        "status": "success",
        "filename": filename,
        "version": version if version is not None else "latest",
        "mime_type": inline_data.mime_type,
        "content": content,
    }
