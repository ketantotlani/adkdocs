import unittest

from src.personalization_tools import (
    get_preferences,
    list_pinned_documents,
    pin_document,
    remember_preference,
)


class FakeToolContext:
    def __init__(self):
        self.state = {}


class PersonalizationToolTests(unittest.TestCase):
    def test_remembers_and_reads_user_preference(self):
        context = FakeToolContext()

        result = remember_preference(
            "focus", "launch blockers", tool_context=context
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            get_preferences(context)["preferences"],
            {"focus": "launch blockers"},
        )

    def test_normalizes_reversed_local_model_arguments(self):
        context = FakeToolContext()

        result = remember_preference(
            "concise bullets", "answer_style", tool_context=context
        )

        self.assertEqual(result["preference"], "answer_style")
        self.assertEqual(context.state["user:answer_style"], "concise bullets")

    def test_pins_each_document_once(self):
        context = FakeToolContext()

        pin_document("Launch_Review_Notes_0818.pdf", context)
        pin_document("Launch_Review_Notes_0818.pdf", context)

        self.assertEqual(
            list_pinned_documents(context)["pinned_documents"],
            ["Launch_Review_Notes_0818.pdf"],
        )


if __name__ == "__main__":
    unittest.main()
