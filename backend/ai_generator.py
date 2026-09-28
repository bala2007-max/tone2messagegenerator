"""
AI Generator Module for Tone-Based Email & Message Generator.
Member 2 Module: LLM Integration using Google GenAI SDK.
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.prompts import build_system_prompt

# Load environment variables from .env file
load_dotenv()


def get_gemini_client():
    """
    Initializes and returns the Google GenAI Client using GEMINI_API_KEY from environment.
    Raises ValueError if the API key is not configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing or unconfigured. "
            "Please add a valid API key to your .env file."
        )
    return genai.Client(api_key=api_key)


def generate_message(input_text: str, message_type: str, tone: str, language: str, length: str) -> str:
    """
    Generates tone-adjusted text using Gemini LLM based on user prompt and parameters.
    
    Args:
        input_text (str): The raw text/intent provided by the user.
        message_type (str): 'Email' or 'Message'
        tone (str): Target tone
        language (str): 'English' or 'Tamil'
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
    
    # Priority list of models to fallback gracefully if a model has high demand (503) or is unavailable
    configured_model = os.getenv("GEMINI_MODEL")
    candidate_models = [configured_model] if configured_model else []
    for candidate in ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]:
        if candidate and candidate not in candidate_models:
            candidate_models.append(candidate)
    
    last_error = None
    for model_name in candidate_models:
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
                # If high demand (503) or rate limit, brief pause before retry or fallback
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt == 0:
                    time.sleep(1)
                    continue
                # For 404 or persistent error, break to next candidate model
                break
                
    raise RuntimeError(f"Gemini API Generation Error: {str(last_error)}")
