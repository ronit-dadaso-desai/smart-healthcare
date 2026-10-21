import hmac
import os
import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/api/chat")
def chat():
    expected = os.environ.get("OLLAMA_PROXY_TOKEN", "")
    supplied = request.headers.get("Authorization", "")

    if not expected or not hmac.compare_digest(
        supplied, f"Bearer {expected}"
    ):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        body = request.get_json(force=True)
        body["stream"] = False
        if body.get("model") != "gemma3:1b":
            return jsonify({"error": "Model not allowed"}), 400

        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            return app.response_class(
                response.read(),
                status=response.status,
                content_type="application/json",
            )

    except urllib.error.URLError:
        return jsonify({"error": "Local Ollama is unavailable"}), 502
    except Exception:
        app.logger.exception("Proxy request failed")
        return jsonify({"error": "Proxy request failed"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
