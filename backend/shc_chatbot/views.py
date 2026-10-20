
import logging

import ollama
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

def health_assistant_view(request):
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            answer = "कृपया तुमचा प्रश्न लिहा. / Please enter your question."

        else:
            history = request.session.get("health_chat_history", [])

            try:
                response = ollama.chat(
                    model="gemma3:1b",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *history[-10:],
                        {"role": "user", "content": question},
                    ],
                )

                answer = response["message"]["content"].strip()

                if not answer:
                    answer = "माफ करा, उत्तर मिळाले नाही. कृपया पुन्हा प्रयत्न करा."
                else:
                    history.extend([
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ])
                    request.session["health_chat_history"] = history[-10:]
                    request.session.modified = True

            except Exception:
                logger.exception("Ollama health assistant request failed.")
                answer = (
                    "माफ करा, स्थानिक AI शी संपर्क होऊ शकला नाही. "
                    "Ollama चालू आहे का ते तपासा."
                )

    return render(
        request,
        "shc_chatbot/assistant.html",
        {
            "answer": answer,
            "question": question,
        },
    )
