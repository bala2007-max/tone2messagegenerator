"""
AI Generator Module for Tone-Based Email & Message Generator.
Member 2 Module: LLM Integration using Google GenAI SDK.
"""

import os
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
    
    # Try gemini-2.5-flash first, fallback to gemini-1.5-flash if needed
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=input_text,
            config=config
        )
        
        if not response or not response.text:
            raise RuntimeError("Received empty response from Gemini API.")
            
        return response.text.strip()
    except Exception as e:
        # Re-raise with informative error message
        raise RuntimeError(f"Gemini API Generation Error: {str(e)}")
