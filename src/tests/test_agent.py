import unittest

from src import agent


class AgentDiscoveryTests(unittest.TestCase):
    def test_package_exposes_root_agent(self):
        self.assertEqual(agent.root_agent.name, "private_document_assistant")
        self.assertEqual(agent.MODEL_ID, "ollama_chat/gemma4:e2b-it-qat")
        self.assertIsInstance(agent.root_agent.instruction, str)
        self.assertIn("{user:focus?}", agent.root_agent.instruction)


if __name__ == "__main__":
    unittest.main()
