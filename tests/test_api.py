"""
Unit Test Suite for Flask Backend REST API (backend/app.py).
Member 2 Module: API Testing & Validation Integration.
Uses an isolated temporary SQLite database and mocks LLM generation.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import sqlite3
from unittest.mock import patch

# Ensure root project path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database.database as db_module
from backend.app import create_app


class TestAPIModule(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary directory, isolated test database, and Flask test client.
        """
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_api_tone_generator.db")
        
        # Patch get_connection to redirect default DB calls to test_db
        self.original_get_connection = db_module.get_connection
        
        def mock_get_connection(db_path=None):
            if db_path is None or db_path == db_module.DEFAULT_DB_PATH:
                target_path = self.test_db
            else:
                target_path = db_path
            conn = sqlite3.connect(target_path)
            conn.row_factory = sqlite3.Row
            return conn

        self.conn_patcher = patch.object(db_module, 'get_connection', side_effect=mock_get_connection)
        self.conn_patcher.start()
        
        # Initialize database schema in isolated test_db
        db_module.create_table(self.test_db)
        
        # Create Flask app and test client
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """
        Clean up test database patcher and temporary directory.
        """
        self.conn_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_get_health(self):
        """TC01: GET /health - Verify server health check status."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)

    @patch('backend.app.generate_message')
    def test_02_post_generate_valid(self, mock_generate):
        """TC02: POST /generate - Verify valid payload processing and AI output mock."""
        mock_generate.return_value = "Dear Team,\n\nI am unable to attend today's meeting.\n\nRegards,\nAlex"
        
        payload = {
            "input_text": "I cannot attend today's meeting.",
            "message_type": "Email",
            "tone": "Formal",
            "language": "English",
            "length": "Medium"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['message_type'], 'Email')
        self.assertEqual(data['data']['tone'], 'Formal')
        self.assertEqual(data['data']['language'], 'English')
        self.assertEqual(data['data']['length'], 'Medium')
        self.assertEqual(data['data']['generated_text'], mock_generate.return_value)
        self.assertGreater(data['data']['id'], 0)

    def test_03_post_generate_empty_input(self):
        """TC03: POST /generate - Verify HTTP 400 when input_text is empty."""
        payload = {
            "input_text": "   ",
            "message_type": "Email",
            "tone": "Formal",
            "language": "English",
            "length": "Medium"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Input text is required")

    def test_04_post_generate_missing_field(self):
        """TC04: POST /generate - Verify HTTP 400 when a required field is missing."""
        payload = {
            "input_text": "I cannot attend today's meeting.",
            "message_type": "Email",
            "tone": "Formal",
            "language": "English"
            # Missing "length"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Missing required field: length", data['error'])

    def test_05_post_generate_invalid_tone(self):
        """TC05: POST /generate - Verify HTTP 400 when tone is invalid."""
        payload = {
            "input_text": "I will be late.",
            "message_type": "Email",
            "tone": "Aggressive_Super_Angry",
            "language": "English",
            "length": "Short"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Invalid tone")

    def test_06_post_generate_invalid_message_type(self):
        """TC06: POST /generate - Verify HTTP 400 when message_type is invalid."""
        payload = {
            "input_text": "I will be late.",
            "message_type": "Telegram_Post",
            "tone": "Casual",
            "language": "English",
            "length": "Short"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Invalid message type")

    def test_07_post_generate_invalid_language(self):
        """TC07: POST /generate - Verify HTTP 400 when language is invalid."""
        payload = {
            "input_text": "I will be late.",
            "message_type": "Message",
            "tone": "Casual",
            "language": "Klingon",
            "length": "Short"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Invalid language")

    def test_08_post_generate_invalid_length(self):
        """TC08: POST /generate - Verify HTTP 400 when length is invalid."""
        payload = {
            "input_text": "I will be late.",
            "message_type": "Message",
            "tone": "Casual",
            "language": "English",
            "length": "Super_Mega_Huge"
        }
        
        response = self.client.post(
            '/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Invalid length")

    @patch('backend.app.generate_message')
    def test_09_get_history(self, mock_generate):
        """TC09: GET /history - Verify retrieving all generated message history."""
        mock_generate.return_value = "Generated response test"
        
        # Populate DB with 2 records via POST /generate
        p1 = {"input_text": "Text 1", "message_type": "Email", "tone": "Formal", "language": "English", "length": "Short"}
        p2 = {"input_text": "Text 2", "message_type": "Message", "tone": "Casual", "language": "Tamil", "length": "Medium"}
        
        self.client.post('/generate', data=json.dumps(p1), content_type='application/json')
        self.client.post('/generate', data=json.dumps(p2), content_type='application/json')
        
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 2)
        # Newest item first (id DESC)
        self.assertEqual(data['data'][0]['input_text'], "Text 2")
        self.assertEqual(data['data'][1]['input_text'], "Text 1")

    @patch('backend.app.generate_message')
    def test_10_get_history_by_id(self, mock_generate):
        """TC10: GET /history/<id> - Verify retrieving specific history item by ID."""
        mock_generate.return_value = "Generated response"
        p = {"input_text": "Single text", "message_type": "Email", "tone": "Friendly", "language": "English", "length": "Detailed"}
        
        gen_resp = self.client.post('/generate', data=json.dumps(p), content_type='application/json')
        rec_id = gen_resp.get_json()['data']['id']
        
        # Fetch valid ID
        response = self.client.get(f'/history/{rec_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], rec_id)
        self.assertEqual(data['data']['input_text'], "Single text")

        # Fetch invalid ID
        inv_response = self.client.get('/history/99999')
        self.assertEqual(inv_response.status_code, 404)
        inv_data = inv_response.get_json()
        self.assertFalse(inv_data['success'])
        self.assertEqual(inv_data['error'], "History record not found")

    @patch('backend.app.generate_message')
    def test_11_delete_history_by_id(self, mock_generate):
        """TC11: DELETE /history/<id> - Verify deleting a specific history item."""
        mock_generate.return_value = "To be deleted"
        p = {"input_text": "Delete me", "message_type": "Message", "tone": "Urgent", "language": "English", "length": "Short"}
        
        gen_resp = self.client.post('/generate', data=json.dumps(p), content_type='application/json')
        rec_id = gen_resp.get_json()['data']['id']
        
        # Delete valid ID
        del_resp = self.client.delete(f'/history/{rec_id}')
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.get_json()['success'])
        
        # Verify it no longer exists
        get_resp = self.client.get(f'/history/{rec_id}')
        self.assertEqual(get_resp.status_code, 404)

        # Delete non-existent ID
        inv_del = self.client.delete('/history/99999')
        self.assertEqual(inv_del.status_code, 404)

    @patch('backend.app.generate_message')
    def test_12_delete_all_history(self, mock_generate):
        """TC12: DELETE /history - Verify clearing all history records."""
        mock_generate.return_value = "Clear test"
        p = {"input_text": "Clear me", "message_type": "Email", "tone": "Polite", "language": "English", "length": "Short"}
        
        self.client.post('/generate', data=json.dumps(p), content_type='application/json')
        self.client.post('/generate', data=json.dumps(p), content_type='application/json')
        
        del_resp = self.client.delete('/history')
        self.assertEqual(del_resp.status_code, 200)
        data = del_resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 2)

        # Verify history list is now empty
        hist_resp = self.client.get('/history')
        self.assertEqual(len(hist_resp.get_json()['data']), 0)


if __name__ == "__main__":
    unittest.main()
