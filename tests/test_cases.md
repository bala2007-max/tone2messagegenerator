# Database Test Cases & Results Documentation

This document outlines the test suite for the SQLite Database Module (`database/database.py`) in the **Tone-Based Email & Message Generator** project.

## Test Results Summary

- **Total Test Cases**: 17
- **Passed**: 17
- **Failed**: 0
- **Status**: ALL PASS

---

## Detailed Test Matrix

| Test ID | Test Description | Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC01** | Database creation | `get_connection(db_path)` | Database file `test_tone_generator.db` is created on filesystem | Database file created and connection established successfully | Pass |
| **TC02** | Table creation | `create_table(db_path)` | Table `message_history` exists with correct 8 columns | Table created with columns: `id`, `input_text`, `message_type`, `tone`, `language`, `length`, `generated_text`, `created_at` | Pass |
| **TC03** | Save history | `input_text="I cannot attend..."`, `message_type="Email"`, `tone="Formal"`, `language="English"`, `length="Medium"`, `generated_text="Dear Sir..."` | Record saved with auto-increment ID > 0 and timestamp populated | Record saved successfully with valid ID and datetime timestamp | Pass |
| **TC04** | Retrieve history | Call `get_history()` after saving 2 records | Returns list of dicts sorted by `id DESC` (newest first) | List of 2 records returned in exact `id DESC` order | Pass |
| **TC05** | Retrieve history by ID | Call `get_history_by_id(row_id)` for valid and invalid IDs | Valid ID returns record dictionary; Invalid ID returns `None` | Record returned matching input ID; `None` returned for ID 9999 | Pass |
| **TC06** | Delete history | Call `delete_history(row_id)` | Selected record removed from database (`get_history_by_id` returns `None`) | Record deleted successfully, subsequent lookup returns `None` | Pass |
| **TC07** | Clear history | Call `clear_history()` on database with multiple records | All records deleted, `get_history()` returns empty list `[]` | 2 records deleted, `get_history()` returned `[]` | Pass |
| **TC08** | Multiple records | Insert 5 records sequentially | Database contains 5 records in `id DESC` order | 5 records retrieved in strictly descending ID order | Pass |
| **TC09** | Empty input | `input_text=""`, `generated_text=""` | Record saved and retrieved with empty strings without error | Empty strings saved and retrieved accurately | Pass |
| **TC10** | Tamil input | `input_text="இன்றைய கூட்டத்தில் என்னால் கலந்து கொள்ள முடியாது."`, `language="தமிழ்"` | Unicode Tamil UTF-8 text saved and retrieved accurately without corruption | Tamil text saved and retrieved with 100% string equality | Pass |
| **TC11** | English input | `input_text="Please send the quarterly financial report."`, `language="English"` | Standard English string saved and retrieved accurately | English string saved and retrieved successfully | Pass |
| **TC12** | Special characters | Special symbols `!@#$%^&*()_+-=[]{}|;':",./<>?`, quotes, and SQL injection string `DROP TABLE message_history; '--` | Parameterized SQL prevents SQL injection; characters stored safely | String stored safely with quotes intact; table was not affected | Pass |
| **TC13** | Long input | 5000 character string for `input_text` and `generated_text` | Long text stored and retrieved without truncation | 5000-character strings saved and retrieved with exact length match | Pass |
| **TC14** | Different tones | Tones: `"Formal"`, `"Informal"`, `"Urgent"`, `"Friendly"`, `"Empathetic"`, `"Professional"` | Each tone value saved and retrieved accurately | All tone values persisted and matched expected output | Pass |
| **TC15** | Different message types | Message types: `"Email"`, `"SMS"`, `"WhatsApp"`, `"LinkedIn Message"`, `"Cover Letter"` | Each message type saved and retrieved accurately | All message types persisted and matched expected output | Pass |
| **TC16** | Different languages | Languages: `"English"`, `"Tamil"`, `"Spanish"`, `"French"`, `"German"` | Each language string saved and retrieved accurately | All language options persisted accurately | Pass |
| **TC17** | Different lengths | Lengths: `"Short"`, `"Medium"`, `"Long"` | Each length string saved and retrieved accurately | All length parameters persisted accurately | Pass |

---

## How to Re-run Tests

Execute the automated test suite anytime using:

```powershell
python -m unittest tests/test_database.py -v
```
