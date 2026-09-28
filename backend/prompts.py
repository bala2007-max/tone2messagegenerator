"""
Prompt Engineering Module for Tone-Based Email & Message Generator.
Member 2 Module: Dynamic System Prompt Construction.
"""

# Supported options validation constants
SUPPORTED_MESSAGE_TYPES = ["Email", "Message"]
SUPPORTED_TONES = [
    "Formal",
    "Professional",
    "Casual",
    "Friendly",
    "Polite",
    "Apologetic",
    "Urgent"
]
SUPPORTED_LANGUAGES = ["English", "Tamil", "Hindi"]
SUPPORTED_LENGTHS = ["Short", "Medium", "Detailed"]

TONE_DESCRIPTIONS = {
    "Formal": "Use respectful, traditional, and structured language suitable for official communication.",
    "Professional": "Use workplace-appropriate, clear, concise, and standard business language.",
    "Casual": "Use relaxed, natural, conversational, and informal language.",
    "Friendly": "Use warm, approachable, kind, and enthusiastic language.",
    "Polite": "Use courteous, considerate, soft-spoken, and highly respectful language.",
    "Apologetic": "Express a sincere and thoughtful apology while keeping the original context and meaning intact.",
    "Urgent": "Clearly communicate high priority and urgency without becoming rude, demanding, or aggressive."
}

LENGTH_DESCRIPTIONS = {
    "Short": "Keep the output concise, direct, and brief (1-3 sentences maximum).",
    "Medium": "Provide a well-balanced response with standard detail (around 1-2 paragraphs).",
    "Detailed": "Provide a complete, comprehensive, and thoroughly structured response."
}


def build_system_prompt(message_type: str, tone: str, language: str, length: str) -> str:
    """
    Constructs a highly tailored system prompt for the Gemini LLM based on user selection.
    
    Args:
        message_type (str): 'Email' or 'Message'
        tone (str): One of the 7 supported tones
        language (str): 'English' or 'Tamil'
        length (str): 'Short', 'Medium', or 'Detailed'
        
    Returns:
        str: Comprehensive system prompt string.
    """
    tone_guide = TONE_DESCRIPTIONS.get(
        tone,
        "Maintain appropriate tone matching user request."
    )
    length_guide = LENGTH_DESCRIPTIONS.get(
        length,
        "Provide appropriate length."
    )
    
    prompt = (
        f"You are an expert AI communication assistant specializing in generating tone-adjusted text.\n\n"
        f"CORE MANDATES:\n"
        f"1. DO NOT alter, lose, or hallucinate the user's original core message or intent.\n"
        f"2. Output ONLY the finalized text. Do NOT include any introductory or concluding meta-chatter, markdown intro/outro (e.g. 'Here is your email:'), or explanation.\n"
        f"3. LANGUAGE: Output must be strictly in {language}. "
    )
    
    if language == "Tamil":
        prompt += (
            "Generate authentic, grammatically correct, natural Tamil phrasing. "
            "Do NOT perform literal word-by-word translation from English. Preserve the intended meaning smoothly.\n"
        )
    elif language == "Hindi":
        prompt += (
            "Generate authentic, grammatically correct, natural Hindi in Devanagari script. "
            "Do NOT perform literal word-by-word translation from English. Preserve the intended meaning smoothly.\n"
        )
    else:
        prompt += "Generate natural, fluent, and idiomatic English.\n"
        
    prompt += (
        f"4. TONE ({tone}): {tone_guide}\n"
        f"5. LENGTH ({length}): {length_guide}\n"
    )
    
    if message_type == "Email":
        prompt += (
            "\nFORMAT REQUIREMENTS (EMAIL):\n"
            "- Include Subject, Greeting, Body, and Closing.\n"
            "- Exact structural template:\n"
            "  Subject: [Clear, relevant subject line]\n\n"
            "  [Greeting, e.g., Dear Sir/Madam, or Hello [Name],]\n\n"
            "  [Body paragraph(s) adhering to tone and length]\n\n"
            "  Regards,\n"
            "  [Generic closing name if user did not provide one, e.g., [Your Name] or Best regards]\n"
            "- Do NOT invent specific personal details unless provided in input.\n"
        )
    else:  # Message
        prompt += (
            "\nFORMAT REQUIREMENTS (MESSAGE):\n"
            "- Do NOT generate a subject line.\n"
            "- Do NOT generate heavy formal headers or footers.\n"
            "- Output a clean, natural chat message suitable for SMS, WhatsApp, or instant messaging.\n"
        )
        
    return prompt
