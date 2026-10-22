
import logging
import os

import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/{model}:generateContent"
)

SYSTEM_PROMPT = """
You are the AI Health Assistant for a Smart Healthcare Platform.

Communication:
- Answer in Marathi when the user writes in Marathi.
- Answer in English when the user writes in English.
- Understand mixed Marathi-English messages.
- Be friendly, clear, concise, and easy to understand.

Medical safety:
- Provide general health information, not a definitive diagnosis.
- Never replace a qualified healthcare professional.
- Do not prescribe medicines or individualized dosages.
- For chest pain, severe breathing difficulty, unconsciousness,
  stroke symptoms, or another emergency, advise immediate medical care.
  In India, call 112 when emergency assistance is needed.
- Do not delay emergency care with unnecessary questions.
- Treat health information as sensitive.
"""


def ask_gemini(messages):
    """Send chat history to Google's hosted Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    contents = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")

        if role == "system":
            continue

        if role == "assistant":
            role = "model"
        elif role != "user":
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        contents.append({
            "role": role,
            "parts": [{"text": content}],
        })

    if not contents:
        raise ValueError("No valid messages to send.")

    response = requests.post(
        GEMINI_API_URL.format(model=model),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 800,
            },
        },
        timeout=60,
    )

    if not response.ok:
        # Log status and response details, but never log the API key.
        logger.error(
            "Gemini API error: HTTP %s; response: %s",
            response.status_code,
            response.text[:1000],
        )
        response.raise_for_status()

    data = response.json()
    candidates = data.get("candidates", [])

    if not candidates:
        raise ValueError("Gemini returned no response candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    answer = "\n".join(
        part["text"]
        for part in parts
        if isinstance(part.get("text"), str)
    ).strip()

    if not answer:
        raise ValueError("Gemini returned an empty answer.")

    return answer


def health_assistant_view(request):
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            answer = "कृपया तुमचा प्रश्न लिहा. / Please enter your question."

        else:
            history = request.session.get("health_chat_history", [])

            if not isinstance(history, list):
                history = []

            history = [
                message
                for message in history
                if isinstance(message, dict)
                and message.get("role") in ("user", "assistant")
                and isinstance(message.get("content"), str)
            ][-10:]

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *history,
                {"role": "user", "content": question},
            ]

            try:
                answer = ask_gemini(messages)

                history.extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ])

                request.session["health_chat_history"] = history[-10:]
                request.session.modified = True

            except requests.Timeout:
                logger.warning("Gemini request timed out.")
                answer = (
                    "माफ करा, AI उत्तर देण्यासाठी जास्त वेळ घेत आहे. "
                    "कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."
                )

            except requests.RequestException:
                logger.exception("Could not connect to Gemini API.")
                answer = (
                    "माफ करा, AI सेवेशी संपर्क होऊ शकला नाही. "
                    "कृपया काही वेळाने पुन्हा प्रयत्न करा."
                )

            except (RuntimeError, ValueError, KeyError):
                logger.exception("Gemini configuration or response error.")
                answer = (
                    "माफ करा, AI configuration मध्ये समस्या आली आहे. "
                    "Render Environment आणि deployment logs तपासा."
                )

            except Exception:
                logger.exception("Unexpected health assistant error.")
                answer = (
                    "माफ करा, काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा."
                )

    return render(
        request,
        "shc_chatbot/assistant.html",
        {
            "answer": answer,
            "question": question,
        },
    )
