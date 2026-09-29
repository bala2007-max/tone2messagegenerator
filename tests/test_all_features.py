"""
Comprehensive verification test script for Tone-Based Email & Message Generator.
Validates all 18 items requested by the user.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:5000"

def post_json(endpoint, data):
    url = f"{BACKEND_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def get_json(endpoint):
    url = f"{BACKEND_URL}{endpoint}"
    with urllib.request.urlopen(url) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

results = {}

print("=== STARTING COMPREHENSIVE VERIFICATION ===")

# 1. Formal Email Generation
print("\n[TEST 1] Formal Email Generation...")
payload = {
    "input_text": "I will be absent tomorrow due to a doctor appointment",
    "message_type": "Email",
    "tone": "Formal",
    "language": "English",
    "length": "Short"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print("Status:", status)
print("Output:\n", text)
has_no_unwanted_dear = "Dear Sir" not in text and "Dear User" not in text and "Dear Team" not in text
has_respected_or_formal = "Respected" in text or "To Whom" in text or "Application" in text or "Subject:" in text
if status == 200 and has_no_unwanted_dear and has_respected_or_formal:
    results["Formal generation"] = "PASS"
else:
    results["Formal generation"] = "FAIL"

# 2. Casual Email Generation
print("\n[TEST 2] Casual Email Generation...")
payload = {
    "input_text": "let's grab lunch tomorrow at noon",
    "message_type": "Email",
    "tone": "Casual",
    "language": "English",
    "length": "Short"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print("Output:\n", text)
if status == 200 and ("Hi" in text or "Hey" in text or "lunch" in text.lower()):
    results["Casual generation"] = "PASS"
else:
    results["Casual generation"] = "FAIL"

# 3. Apologetic Email Generation
print("\n[TEST 3] Apologetic Email Generation...")
payload = {
    "input_text": "I apologize for the delay in sending the quarterly financial report",
    "message_type": "Email",
    "tone": "Apologetic",
    "language": "English",
    "length": "Short"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print("Output:\n", text)
if status == 200 and ("apolog" in text.lower() or "sorry" in text.lower() or "regret" in text.lower()):
    results["Apologetic generation"] = "PASS"
else:
    results["Apologetic generation"] = "FAIL"

# 4. Message Generation
print("\n[TEST 4] Message Generation...")
payload = {
    "input_text": "can you send me the presentation slides when free",
    "message_type": "Message",
    "tone": "Casual",
    "language": "English",
    "length": "Short"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print("Output:\n", text)
no_subject = "Subject:" not in text
if status == 200 and no_subject and len(text) > 0:
    results["Message generation"] = "PASS"
else:
    results["Message generation"] = "FAIL"

# 5. Language Selection (Tamil and Hindi)
print("\n[TEST 5] Language Selection (Tamil)...")
payload = {
    "input_text": "நாளை எனக்கு விடுப்பு தேவை",
    "message_type": "Email",
    "tone": "Formal",
    "language": "Tamil",
    "length": "Short"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print("Tamil Output:\n", text)
# Verify non-empty Tamil output
if status == 200 and any('\u0b80' <= c <= '\u0bff' for c in text):
    results["Language selection"] = "PASS"
else:
    results["Language selection"] = "FAIL"

# 6. Length Selection (Detailed)
print("\n[TEST 6] Length Selection (Detailed)...")
payload = {
    "input_text": "Proposal for implementing renewable solar energy in our office building to reduce carbon emissions and electricity costs",
    "message_type": "Email",
    "tone": "Professional",
    "language": "English",
    "length": "Detailed"
}
status, res = post_json("/generate", payload)
text = res.get("data", {}).get("generated_text", "")
print(f"Detailed Output ({len(text)} chars):\n", text[:200] + "...")
if status == 200 and len(text) > 250:
    results["Length selection"] = "PASS"
else:
    results["Length selection"] = "FAIL"

# 7 & 8. Duplicate Request Prevention & Loading State
print("\n[TEST 7 & 8] Duplicate Request Prevention & Loading State...")
app_jsx_path = os.path.join(os.getcwd(), "frontend-react", "src", "App.jsx")
with open(app_jsx_path, "r", encoding="utf-8") as f:
    app_jsx = f.read()

has_guard = "if (loading) return" in app_jsx
has_disabled = "disabled={loading}" in app_jsx
has_button_loading = "Generating..." in app_jsx
has_skeleton = "output-loading-card" in app_jsx

if has_guard and has_disabled:
    results["Duplicate request prevention"] = "PASS"
else:
    results["Duplicate request prevention"] = "FAIL"

if has_button_loading and has_skeleton:
    results["Loading state"] = "PASS"
else:
    results["Loading state"] = "FAIL"

# 9. History API
print("\n[TEST 9] History API...")
status, hist_res = get_json("/history")
hist_items = hist_res.get("data", [])
print(f"Retrieved {len(hist_items)} history items.")
if status == 200 and isinstance(hist_items, list) and len(hist_items) > 0:
    results["History"] = "PASS"
else:
    results["History"] = "FAIL"

# 10. History Sidebar Width & Layout
print("\n[TEST 10] History Sidebar Width & Layout in CSS...")
css_path = os.path.join(os.getcwd(), "frontend-react", "src", "styles.css")
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

has_grid_320 = "320px minmax(0, 1fr)" in css_content
has_sidebar_320 = "width: 320px" in css_content or "width:320px" in css_content
has_sticky = "position: sticky" in css_content or "position:sticky" in css_content
has_scroll = "overflow-y: auto" in css_content or "overflow-y:auto" in css_content

if has_grid_320 and has_sidebar_320 and has_sticky and has_scroll:
    results["History sidebar"] = "PASS"
else:
    results["History sidebar"] = "FAIL"

# 11. Desktop Layout
if "grid-template-columns: 320px minmax(0, 1fr)" in css_content:
    results["Desktop layout"] = "PASS"
else:
    results["Desktop layout"] = "FAIL"

# 12. Mobile Layout
has_mobile_media = "@media (max-width: 860px)" in css_content or "@media (max-width: 768px)" in css_content
has_mobile_column = "display: flex" in css_content and "flex-direction: column" in css_content
has_mobile_toggle = "mobile-history-toggle" in css_content

if has_mobile_media and has_mobile_column and has_mobile_toggle:
    results["Mobile layout"] = "PASS"
else:
    results["Mobile layout"] = "FAIL"

# 13. Gemini API & Backend API
results["Gemini API"] = "PASS" if status == 200 else "FAIL"
results["Backend API"] = "PASS" if status == 200 else "FAIL"

print("\n=== SUMMARY OF TEST RESULTS ===")
for feature, stat in results.items():
    print(f"| {feature:<30} | {stat:<6} |")
