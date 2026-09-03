import unittest

from src.document_tools import (
    get_document_info,
    list_documents,
    read_document,
    search_documents,
)


class DocumentToolTests(unittest.TestCase):
    def test_workspace_has_sample_documents(self):
        result = list_documents()
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["document_count"], 4)

    def test_read_pdf(self):
        result = read_document("Atlas_Product_Brief_v3.pdf")
        self.assertEqual(result["status"], "success")
        self.assertIn("Project Atlas", result["content"])

    def test_search_across_documents(self):
        result = search_documents("security review")
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["match_count"], 2)

    def test_path_escape_is_blocked(self):
        result = read_document("../agent.py")
        self.assertEqual(result["status"], "error")

    def test_document_info(self):
        result = get_document_info("June_Customer_Research.pdf")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["type"], "pdf")


if __name__ == "__main__":
    unittest.main()
