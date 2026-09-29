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
    "Formal": "Use respectful, dignified, and structured language suitable for official communication and institutional correspondence.",
    "Professional": "Use workplace-appropriate, clear, concise, and standard modern business language.",
    "Casual": "Use relaxed, natural, conversational, and everyday language without corporate jargon or forced formality.",
    "Friendly": "Use warm, approachable, kind, and positive language.",
    "Polite": "Use courteous, considerate, tactful, and highly respectful language.",
    "Apologetic": "Express a sincere, accountable, and thoughtful apology without being defensive or sounding robotic, keeping the original context intact.",
    "Urgent": "Clearly communicate high priority and time sensitivity clearly and professionally without becoming rude or aggressive."
}

LENGTH_DESCRIPTIONS = {
    "Short": "Keep the output strictly concise, direct, and brief (1-3 sentences maximum). Get straight to the point.",
    "Medium": "Provide a well-balanced response with standard detail (around 1-2 paragraphs).",
    "Detailed": "Provide a complete, comprehensive, and thoroughly structured response with appropriate elaboration."
}


def build_system_prompt(message_type: str, tone: str, language: str, length: str) -> str:
    """
    Constructs a highly tailored system prompt for the Gemini LLM based on user selection.
    
    Args:
        message_type (str): 'Email' or 'Message'
        tone (str): One of the 7 supported tones
        language (str): 'English', 'Tamil', or 'Hindi'
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
            "- Include Subject, Greeting/Salutation, Body, and Closing.\n"
            "- Exact structural template:\n"
            "  Subject: [Clear, relevant subject line]\n\n"
            "  [Context-appropriate Salutation / Greeting]\n\n"
            "  [Body paragraph(s) adhering strictly to selected tone and length]\n\n"
            "  Regards,\n"
            "  [Generic closing name if user did not provide one, e.g., [Your Name] or Best regards]\n\n"
            "SALUTATION & GREETING RULES (EMAIL):\n"
            "- If the user specified a recipient name or specific title in their input:\n"
            "  * Address them respectfully based on tone: e.g., 'Respected Dr. Sharma,' (Formal/Polite), 'Dear Mr. Davis,' (Professional/Formal with named person), 'Hi Sarah,' (Casual/Friendly).\n"
            "- If NO recipient name is provided in the input, do NOT use generic 'Dear Sir/Madam', 'Dear User', or 'Dear Team':\n"
            "  * FORMAL: Use a dignified, professional opening such as 'Respected Sir/Madam,' or 'Respected Team,'. Never use 'Dear Sir/Madam' or 'Dear User'.\n"
            "  * PROFESSIONAL: Use a modern workplace opening such as 'Greetings,', 'Good morning / afternoon,', or 'Hello Team,'.\n"
            "  * CASUAL: Use a natural, relaxed opening such as 'Hi there,', 'Hey team,', or start directly. Do NOT force formal greetings.\n"
            "  * FRIENDLY: Use a warm greeting such as 'Hello everyone,', 'Hi there,', or 'Hope you are doing well!'.\n"
            "  * POLITE: Use a courteous opening such as 'Respected Sir/Madam,' or 'Greetings,'.\n"
            "  * APOLOGETIC: Start with a sincere, respectful opening appropriate to the situation (e.g. 'Respected Sir/Madam,' or addressing recipient directly, followed immediately by sincere acknowledgment of the issue).\n"
            "  * URGENT: Use a direct, prioritized opening such as 'Attention: [Team/Recipient],' or 'Immediate Attention Required:'.\n"
            "- Language-specific email salutations:\n"
            "  * In Tamil: For Formal/Polite use 'மதிப்பிற்குரிய ஐயா/அம்மா,' (Respected Sir/Madam) or 'அனைவருக்கும் வணக்கம்,'. For Casual/Friendly use 'வணக்கம்,'.\n"
            "  * In Hindi: For Formal/Polite use 'आदरणीय महोदय/महोदया,' (Respected Sir/Madam) or 'सादर प्रणाम,'. For Casual/Friendly use 'नमस्ते,'.\n"
            "- Do NOT invent specific personal details unless provided in the input.\n"
        )
    else:  # Message
        prompt += (
            "\nFORMAT REQUIREMENTS (MESSAGE / CHAT):\n"
            "- Do NOT generate a subject line.\n"
            "- Do NOT generate heavy formal headers, email-style greetings like 'Dear Sir/Madam' or 'Respected Sir/Madam', or email sign-offs ('Regards, [Your Name]').\n"
            "- Output a clean, natural chat message suitable for SMS, WhatsApp, Slack, or instant messaging.\n"
            "- For Casual/Friendly messages: Use natural conversational phrasing (e.g., 'Hey,', 'Hi,').\n"
            "- For Formal/Professional messages: Keep the message polite, clear, and respectful without turning it into an email.\n"
            "- For Apologetic messages: Express sincere accountability directly and naturally.\n"
            "- Language-specific chat greetings:\n"
            "  * In Tamil: 'வணக்கம்' or direct conversational phrasing.\n"
            "  * In Hindi: 'नमस्ते' or direct conversational phrasing.\n"
        )
        
    return prompt
