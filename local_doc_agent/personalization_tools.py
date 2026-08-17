from typing import Any
from google.adk.tools import ToolContext


ALLOWED_PREFERENCES = {
    "focus",
    "answer_style",
    "detail_level",
    "citation_style",
}


def _normalize_preference(preference: str, value: str) -> tuple[str, str]:
    """
    Normalize imperfect tool arguments from a local model.

    The model may sometimes pass:
      preference="launch blockers and customer feedback"
      value="focus"

    or it may put the whole preference text in `preference`.

    We normalize those cases into:
      category="focus"
      value="launch blockers and customer feedback"
    """
    raw_preference = (preference or "").strip()
    raw_value = (value or "").strip()

    p = raw_preference.lower()
    v = raw_value.lower()

    # Ideal call: preference="focus", value="..."
    if p in ALLOWED_PREFERENCES:
        return p, raw_value

    # Common local-model mistake: arguments reversed.
    if v in ALLOWED_PREFERENCES:
        return v, raw_preference

    # If the model supplied free-form text instead of a category,
    # infer the most useful category.
    combined = f"{raw_preference} {raw_value}".lower()

    if "citation" in combined or "source" in combined:
        category = "citation_style"
    elif any(word in combined for word in ["detail", "brief", "concise", "verbose", "depth"]):
        category = "detail_level"
    elif any(word in combined for word in ["style", "format", "bullet", "paragraph"]):
        category = "answer_style"
    else:
        category = "focus"

    stored_value = raw_value or raw_preference
    return category, stored_value


def remember_preference(
    preference: str,
    value: str = "",
    tool_context: ToolContext = None,
) -> dict[str, Any]:
    """
    Save a durable user preference across sessions.

    `preference` should ideally be one of:
    focus, answer_style, detail_level, citation_style.

    `value` contains the preference text.

    The function also tolerates imperfect argument ordering from local models.
    """
    if tool_context is None:
        return {"status": "error", "message": "Tool context is unavailable."}

    category, stored_value = _normalize_preference(preference, value)

    if not stored_value:
        return {"status": "error", "message": "Preference value cannot be empty."}

    tool_context.state[f"user:{category}"] = stored_value

    return {
        "status": "success",
        "preference": category,
        "value": stored_value,
    }


def get_preferences(tool_context: ToolContext) -> dict[str, Any]:
    """Return the user's saved document-assistant preferences."""
    preferences = {}

    for key in sorted(ALLOWED_PREFERENCES):
        value = tool_context.state.get(f"user:{key}")
        if value is not None:
            preferences[key] = value

    return {
        "status": "success",
        "preferences": preferences,
    }


def pin_document(
    relative_path: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Pin a document so the assistant remembers it as important across sessions."""
    path = (relative_path or "").strip()

    if not path:
        return {"status": "error", "message": "Document path cannot be empty."}

    current = tool_context.state.get("user:pinned_documents", [])
    if not isinstance(current, list):
        current = []

    if path not in current:
        current = [*current, path]
        tool_context.state["user:pinned_documents"] = current

    return {
        "status": "success",
        "pinned_documents": current,
    }


def list_pinned_documents(tool_context: ToolContext) -> dict[str, Any]:
    """List documents the user previously pinned as important."""
    current = tool_context.state.get("user:pinned_documents", [])

    if not isinstance(current, list):
        current = []

    return {
        "status": "success",
        "pinned_documents": current,
    }
