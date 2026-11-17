
from config.settings import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    AI_PROVIDER,
    AI_MODEL
)


def generate_ai_response(system_prompt, user_prompt):

    if AI_PROVIDER == "gemini":

        from google import genai

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        response = client.models.generate_content(
            model=AI_MODEL,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": 0.4,
                "max_output_tokens": 3000
            }
        )

        return response.text

    elif AI_PROVIDER == "groq":

        from groq import Groq

        client = Groq(
            api_key=GROQ_API_KEY
        )

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.4,
            max_tokens=3000
        )

        return response.choices[0].message.content

    else:
        raise ValueError("Unsupported AI provider")
