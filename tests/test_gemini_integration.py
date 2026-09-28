"""
Integration Test for Google Gemini API Client and AI Generator.
Verifies client initialization, model fallback, and live generation.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.ai_generator import (
    get_gemini_client,
    get_model_candidates,
    generate_message
)


class TestGeminiIntegration(unittest.TestCase):

    def test_01_client_initialization(self):
        """Verify get_gemini_client initializes successfully when API key is set."""
        client = get_gemini_client()
        self.assertIsNotNone(client, "Gemini client should be created")

    def test_02_model_candidates(self):
        """Verify model candidates contain verified supported models."""
        candidates = get_model_candidates()
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)
        self.assertIn("gemini-3.6-flash", candidates)

    def test_03_live_generation_english(self):
        """Verify real generation with Gemini API for an English message."""
        output = generate_message(
            input_text="Need sick leave today",
            message_type="Message",
            tone="Formal",
            language="English",
            length="Short"
        )
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 5)

    def test_04_live_generation_email_structure(self):
        """Verify real generation with Gemini API for an Email message."""
        output = generate_message(
            input_text="Send the financial report by 5 PM",
            message_type="Email",
            tone="Professional",
            language="English",
            length="Short"
        )
        self.assertIsInstance(output, str)
        self.assertIn("Subject:", output)

    def test_05_missing_api_key_handling(self):
        """Verify clear ValueError when GEMINI_API_KEY is empty."""
        original_key = os.environ.get("GEMINI_API_KEY", "")
        try:
            os.environ["GEMINI_API_KEY"] = ""
            with self.assertRaises(ValueError) as ctx:
                get_gemini_client()
            self.assertIn("GEMINI_API_KEY is missing", str(ctx.exception))
        finally:
            os.environ["GEMINI_API_KEY"] = original_key


if __name__ == "__main__":
    unittest.main()
