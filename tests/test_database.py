"""
Unit Test Suite for SQLite Database Module (database/database.py).
Member 3 Module: Database Testing.
Uses an isolated temporary database to prevent modifying production database.
"""

import os
import shutil
import tempfile
import unittest
import sys

# Ensure database package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import (
    get_connection,
    create_table,
    save_history,
    get_history,
    get_history_by_id,
    delete_history,
    clear_history
)


class TestDatabaseModule(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary directory and database file for each test case.
        """
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_tone_generator.db")
        create_table(self.test_db)

    def tearDown(self):
        """
        Clean up the temporary directory and test database after each test.
        """
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_database_creation(self):
        """TC01: Verify Database creation."""
        self.assertTrue(os.path.exists(self.test_db), "Test database file should exist.")
        conn = get_connection(self.test_db)
        self.assertIsNotNone(conn, "Database connection should be established.")
        conn.close()

    def test_02_table_creation(self):
        """TC02: Verify Table creation and schema."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(message_history)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()

        expected_columns = [
            "id", "input_text", "message_type", "tone",
            "language", "length", "generated_text", "created_at"
        ]
        for col in expected_columns:
            self.assertIn(col, columns, f"Column '{col}' should exist in message_history table.")

    def test_03_save_history(self):
        """TC03: Verify Save history."""
        row_id = save_history(
            input_text="I cannot attend today's meeting.",
            message_type="Email",
            tone="Formal",
            language="English",
            length="Medium",
            generated_text="Dear Sir, I am unable to attend today's meeting.",
            db_path=self.test_db
        )
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)

        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(record["input_text"], "I cannot attend today's meeting.")
        self.assertEqual(record["message_type"], "Email")
        self.assertEqual(record["tone"], "Formal")
        self.assertEqual(record["language"], "English")
        self.assertEqual(record["length"], "Medium")
        self.assertEqual(record["generated_text"], "Dear Sir, I am unable to attend today's meeting.")
        self.assertIsNotNone(record["created_at"])

    def test_04_retrieve_history(self):
        """TC04: Verify Retrieve history (ORDER BY id DESC)."""
        id1 = save_history("First input", "Email", "Formal", "English", "Short", "First text", db_path=self.test_db)
        id2 = save_history("Second input", "SMS", "Casual", "English", "Short", "Second text", db_path=self.test_db)

        history = get_history(db_path=self.test_db)
        self.assertEqual(len(history), 2)
        # Newest record first
        self.assertEqual(history[0]["id"], id2)
        self.assertEqual(history[1]["id"], id1)

    def test_05_retrieve_history_by_id(self):
        """TC05: Verify Retrieve history by ID."""
        row_id = save_history("Meeting update", "Email", "Professional", "English", "Medium", "Update content", db_path=self.test_db)
        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], row_id)
        self.assertEqual(record["input_text"], "Meeting update")

        non_existent = get_history_by_id(9999, db_path=self.test_db)
        self.assertIsNone(non_existent)

    def test_06_delete_history(self):
        """TC06: Verify Delete history."""
        row_id = save_history("Delete me", "Note", "Casual", "English", "Short", "To be deleted", db_path=self.test_db)
        result = delete_history(row_id, db_path=self.test_db)
        self.assertTrue(result)

        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertIsNone(record)

        # Deleting non-existent record should return False
        result_non_existent = delete_history(9999, db_path=self.test_db)
        self.assertFalse(result_non_existent)

    def test_07_clear_history(self):
        """TC07: Verify Clear history."""
        save_history("Text 1", "Email", "Formal", "English", "Short", "Gen 1", db_path=self.test_db)
        save_history("Text 2", "SMS", "Casual", "English", "Short", "Gen 2", db_path=self.test_db)
        
        deleted_count = clear_history(db_path=self.test_db)
        self.assertEqual(deleted_count, 2)

        history = get_history(db_path=self.test_db)
        self.assertEqual(len(history), 0)

    def test_08_multiple_records(self):
        """TC08: Verify Multiple records insertion and retrieval."""
        for i in range(1, 6):
            save_history(f"Input {i}", "Email", "Friendly", "English", "Short", f"Output {i}", db_path=self.test_db)

        history = get_history(db_path=self.test_db)
        self.assertEqual(len(history), 5)
        # Check decreasing ID sequence (ORDER BY id DESC)
        ids = [item["id"] for item in history]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_09_empty_input(self):
        """TC09: Verify handling of empty input fields."""
        row_id = save_history("", "WhatsApp", "Polite", "English", "Short", "", db_path=self.test_db)
        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(record["input_text"], "")
        self.assertEqual(record["generated_text"], "")

    def test_10_tamil_input(self):
        """TC10: Verify Tamil text support (Unicode UTF-8)."""
        tamil_input = "இன்றைய கூட்டத்தில் என்னால் கலந்து கொள்ள முடியாது."
        tamil_output = "அன்புள்ள ஐயா, இன்றைய கூட்டத்தில் என்னால் கலந்து கொள்ள இயலவில்லை."
        row_id = save_history(tamil_input, "மின்னஞ்சல்", "முறையான", "தமிழ்", "நடுத்தர", tamil_output, db_path=self.test_db)

        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(record["input_text"], tamil_input)
        self.assertEqual(record["generated_text"], tamil_output)
        self.assertEqual(record["language"], "தமிழ்")

    def test_11_english_input(self):
        """TC11: Verify English text input."""
        row_id = save_history("Please send the quarterly financial report.", "Email", "Professional", "English", "Short", "Dear Team, please share the quarterly financial report.", db_path=self.test_db)
        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(record["language"], "English")

    def test_12_special_characters(self):
        """TC12: Verify Special characters, quotes, and SQL injection attempt handling."""
        special_input = "Hello! @#$%^&*()_+-=[]{}|;':\",./<>? `~ \n\t DROP TABLE message_history; '--"
        special_output = "Output with 'single' and \"double\" quotes & <html>tags</html>."
        row_id = save_history(special_input, "Email", "Assertive", "English", "Long", special_output, db_path=self.test_db)

        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(record["input_text"], special_input)
        self.assertEqual(record["generated_text"], special_output)

        # Verify table was not dropped by SQL injection attempt
        history = get_history(db_path=self.test_db)
        self.assertGreaterEqual(len(history), 1)

    def test_13_long_input(self):
        """TC13: Verify Long input handling (5000+ characters)."""
        long_input = "A" * 5000
        long_output = "B" * 5000
        row_id = save_history(long_input, "Document", "Detailed", "English", "Very Long", long_output, db_path=self.test_db)

        record = get_history_by_id(row_id, db_path=self.test_db)
        self.assertEqual(len(record["input_text"]), 5000)
        self.assertEqual(len(record["generated_text"]), 5000)

    def test_14_different_tones(self):
        """TC14: Verify Different tones support."""
        tones = ["Formal", "Informal", "Urgent", "Friendly", "Empathetic", "Professional"]
        for tone in tones:
            row_id = save_history("Sample input", "Email", tone, "English", "Medium", f"Sample text in {tone} tone.", db_path=self.test_db)
            record = get_history_by_id(row_id, db_path=self.test_db)
            self.assertEqual(record["tone"], tone)

    def test_15_different_message_types(self):
        """TC15: Verify Different message types support."""
        types = ["Email", "SMS", "WhatsApp", "LinkedIn Message", "Cover Letter"]
        for msg_type in types:
            row_id = save_history("Sample prompt", msg_type, "Formal", "English", "Medium", f"Content for {msg_type}.", db_path=self.test_db)
            record = get_history_by_id(row_id, db_path=self.test_db)
            self.assertEqual(record["message_type"], msg_type)

    def test_16_different_languages(self):
        """TC16: Verify Different languages support."""
        languages = ["English", "Tamil", "Spanish", "French", "German"]
        for lang in languages:
            row_id = save_history("Hello", "SMS", "Casual", lang, "Short", f"Greeting in {lang}", db_path=self.test_db)
            record = get_history_by_id(row_id, db_path=self.test_db)
            self.assertEqual(record["language"], lang)

    def test_17_different_lengths(self):
        """TC17: Verify Different lengths support."""
        lengths = ["Short", "Medium", "Long"]
        for length in lengths:
            row_id = save_history("Brief note", "Email", "Formal", "English", length, f"Content length: {length}", db_path=self.test_db)
            record = get_history_by_id(row_id, db_path=self.test_db)
            self.assertEqual(record["length"], length)


if __name__ == "__main__":
    unittest.main()
