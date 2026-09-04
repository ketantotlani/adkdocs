import unittest
from types import SimpleNamespace

from src import agent


class AgentDiscoveryTests(unittest.TestCase):
    def test_package_exposes_root_agent(self):
        self.assertEqual(agent.root_agent.name, "private_document_assistant")
        self.assertEqual(agent.MODEL_ID, "ollama_chat/gemma4:e2b-it-qat")
        self.assertIsInstance(agent.root_agent.instruction, str)
        self.assertIn("{user:focus?}", agent.root_agent.instruction)


class FakeCallbackContext:
    def __init__(self):
        self.session = SimpleNamespace(
            events=[
                SimpleNamespace(author="user"),
                SimpleNamespace(author="private_document_assistant"),
            ]
        )
        self.saved_events = None

    async def add_events_to_memory(self, *, events):
        self.saved_events = events


class MemoryCallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_user_events_are_saved_to_memory(self):
        context = FakeCallbackContext()

        await agent.auto_save_session_to_memory(context)

        self.assertEqual(len(context.saved_events), 1)
        self.assertEqual(context.saved_events[0].author, "user")


if __name__ == "__main__":
    unittest.main()
