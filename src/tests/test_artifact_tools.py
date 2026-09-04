import unittest

import google.genai.types as types

from src.artifact_tools import load_saved_brief


class FakeToolContext:
    def __init__(self, artifact):
        self.artifact = artifact
        self.calls = []

    async def load_artifact(self, filename, version=None):
        self.calls.append((filename, version))
        return self.artifact


class LoadSavedBriefTests(unittest.IsolatedAsyncioTestCase):
    async def test_loads_latest_markdown_artifact(self):
        artifact = types.Part.from_bytes(
            data=b"# Medium draft\n\nLocal-first content.",
            mime_type="text/markdown",
        )
        context = FakeToolContext(artifact)

        result = await load_saved_brief("Medium_Draft.md", context)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "# Medium draft\n\nLocal-first content.")
        self.assertEqual(result["mime_type"], "text/markdown")
        self.assertEqual(context.calls, [("Medium_Draft.md", None)])

    async def test_rejects_path_traversal(self):
        context = FakeToolContext(None)

        result = await load_saved_brief("../private.md", context)

        self.assertEqual(result["status"], "error")
        self.assertEqual(context.calls, [])

    async def test_reports_missing_artifact(self):
        context = FakeToolContext(None)

        result = await load_saved_brief("Missing.md", context, version=2)

        self.assertEqual(result["status"], "error")
        self.assertEqual(context.calls, [("Missing.md", 2)])


if __name__ == "__main__":
    unittest.main()
