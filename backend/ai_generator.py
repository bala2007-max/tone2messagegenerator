"""
AI Generator Module for Tone-Based Email & Message Generator.
Member 2 Module: LLM Integration using Google GenAI SDK.
"""

import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Locate project directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Load environment variables: check project root first, then parent directory, then system
load_dotenv(os.path.join(ROOT_DIR, ".env"))
load_dotenv(os.path.join(ROOT_DIR, "..", ".env"))
load_dotenv()

from backend.prompts import build_system_prompt

# Currently supported and verified Gemini models prioritized for speed and availability
DEFAULT_FALLBACK_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash"
]


def get_gemini_client():
    """
    Initializes and returns the Google GenAI Client using GEMINI_API_KEY from environment.
    Raises ValueError if the API key is missing or unconfigured.
    """
    raw_key = os.getenv("GEMINI_API_KEY", "")
    api_key = raw_key.strip().strip("'\"")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is missing or unconfigured. "
            "Please provide a valid Gemini API key in your .env file."
        )
    return genai.Client(api_key=api_key)


def get_model_candidates():
    """
    Returns prioritized list of valid models to try.
    Checks GEMINI_MODEL env var first, followed by verified supported fallback models.
    """
    configured = os.getenv("GEMINI_MODEL", "").strip().strip("'\"")
    models = []
    if configured:
        models.append(configured)
    for model in DEFAULT_FALLBACK_MODELS:
        if model not in models:
            models.append(model)
    return models


def generate_message(input_text: str, message_type: str, tone: str, language: str, length: str) -> str:
    """
    Generates tone-adjusted text using Gemini LLM based on user prompt and parameters.
    
    Args:
        input_text (str): The raw text/intent provided by the user.
        message_type (str): 'Email' or 'Message'
        tone (str): Target tone
        language (str): 'English', 'Tamil', or 'Hindi'
        length (str): Output length preference
        
    Returns:
        str: Generated message text.
    """
    system_instruction = build_system_prompt(
        message_type=message_type,
        tone=tone,
        language=language,
        length=length
    )
    
    client = get_gemini_client()
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
    )
    
    candidate_models = get_model_candidates()
    last_error = None
    
    for model_name in candidate_models:
        # Try candidate model up to 2 times for transient errors
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=input_text,
                    config=config
                )
                
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_str = str(e)
                
                # Check for Authentication errors (401 / 403)
                if "401" in err_str or "403" in err_str or "API_KEY_INVALID" in err_str or "PERMISSION_DENIED" in err_str:
                    raise ValueError(
                        "Gemini API Authentication Failed: Invalid or unauthorized GEMINI_API_KEY. "
                        "Please verify your API key in .env."
                    )
                
                # If quota exhausted (429), retrying the same model with 1s sleep won't help;
                # immediately switch to the next fallback candidate model for instant speed.
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    break
                
                # For transient service overload (503 / UNAVAILABLE), retry once quickly then fall through
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    if attempt == 0:
                        time.sleep(0.5)
                        continue
                    break
                
                # If model not found or deprecated (404), switch immediately to next candidate
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break
                    
                # Other unexpected exceptions, move to next candidate model
                break
                
    # If all candidate models were exhausted
    err_msg = str(last_error) if last_error else "Unknown generation error"
    if "404" in err_msg or "NOT_FOUND" in err_msg:
        raise RuntimeError(
            f"Gemini API Error (404 Not Found): The requested Gemini model was not found or is unavailable to this API key."
        )
    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
        raise RuntimeError(
            "Gemini API Rate Limit Exceeded: Free tier quota has been reached. Please wait a moment before trying again."
        )
    if "503" in err_msg or "UNAVAILABLE" in err_msg:
        raise RuntimeError(
            "Gemini API Service Unavailable: The model is currently experiencing high demand. Please try again shortly."
        )
    raise RuntimeError(f"Gemini API Generation Error: {err_msg}")
