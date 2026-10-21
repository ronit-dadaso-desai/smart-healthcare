import logging
import os

import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)

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


def ask_local_ollama(messages):
    """Send a chat request to the token-protected local Ollama proxy."""
    ollama_host = os.environ.get("OLLAMA_HOST", "").rstrip("/")
    proxy_token = os.environ.get("OLLAMA_PROXY_TOKEN", "")

    if not ollama_host or not proxy_token:
        raise RuntimeError(
            "OLLAMA_HOST or OLLAMA_PROXY_TOKEN environment variable is missing."
        )

    response = requests.post(
        f"{ollama_host}/api/chat",
        headers={
            "Authorization": f"Bearer {proxy_token}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gemma3:1b",
            "messages": messages,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict) or not isinstance(data.get("message"), dict):
        raise ValueError("Invalid response received from the Ollama proxy.")

    return data


def health_assistant_view(request):
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            answer = "कृपया तुमचा प्रश्न लिहा. / Please enter your question."

        else:
            history = request.session.get("health_chat_history", [])

            # Keep only valid user/assistant messages from the session.
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
                response = ask_local_ollama(messages)
                answer = response["message"]["content"].strip()

                if not answer:
                    answer = (
                        "माफ करा, उत्तर मिळाले नाही. कृपया पुन्हा प्रयत्न करा."
                    )
                else:
                    history.extend([
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ])

                    request.session["health_chat_history"] = history[-10:]
                    request.session.modified = True

            except requests.Timeout:
                logger.warning("Local Ollama request timed out.")
                answer = (
                    "माफ करा, AI उत्तर देण्यासाठी जास्त वेळ घेत आहे. "
                    "कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."
                )

            except requests.RequestException:
                logger.exception("Could not connect to the Ollama proxy.")
                answer = (
                    "माफ करा, AI सेवेशी संपर्क होऊ शकला नाही. "
                    "Ollama, proxy आणि Cloudflare Tunnel चालू आहेत का ते तपासा."
                )

            except (RuntimeError, ValueError, KeyError):
                logger.exception("Ollama configuration or response error.")
                answer = (
                    "माफ करा, AI configuration मध्ये समस्या आली आहे. "
                    "कृपया administrator शी संपर्क साधा."
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
