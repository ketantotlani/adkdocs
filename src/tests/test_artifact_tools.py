import unittest

import google.genai.types as types

from src.artifact_tools import _infer_sources, load_saved_brief, save_brief


class FakeToolContext:
    def __init__(self, artifact):
        self.artifact = artifact
        self.calls = []

    async def load_artifact(self, filename, version=None):
        self.calls.append((filename, version))
        return self.artifact

    async def save_artifact(self, filename, artifact):
        self.calls.append((filename, artifact))
        self.artifact = artifact
        return 0


class SaveBriefTests(unittest.IsolatedAsyncioTestCase):
    async def test_does_not_duplicate_matching_title(self):
        context = FakeToolContext(None)

        result = await save_brief(
            "# Final QA Brief\n\nThe pilot target is 22 September.",
            context,
            title="Final QA Brief",
            sources=["Launch_Review_Notes_0818.pdf"],
        )

        saved_text = context.artifact.inline_data.data.decode("utf-8")
        self.assertEqual(result["status"], "success")
        self.assertEqual(saved_text.count("# Final QA Brief"), 1)
        self.assertIn("- Launch_Review_Notes_0818.pdf", saved_text)


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


class InferSourcesTests(unittest.TestCase):
    def test_extracts_filenames_without_surrounding_prose(self):
        content = (
            "Based on Atlas_Product_Brief_v3.pdf and release-checklist.md."
        )

        self.assertEqual(
            _infer_sources(content),
            ["Atlas_Product_Brief_v3.pdf", "release-checklist.md"],
        )


if __name__ == "__main__":
    unittest.main()
