"""Offline Watson-compatible emotion stub for UI verification ONLY.

This server is NOT IBM Watson and its scores are NOT Watson output. It exists
only so the Flask frontend can be exercised in an environment where the IBM
Skills Network lab endpoint is unreachable. It speaks the same HTTP/JSON shape
as the Watson NLP EmotionPredict service so the application code path is real.

Usage:
    python3 tools/watson_stub.py 9099
    WATSON_EMOTION_URL=http://127.0.0.1:9099/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict \
        python3 server.py
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

LEXICON = {
    "anger": ("angry", "mad", "furious", "rage", "annoyed", "hate"),
    "disgust": ("disgust", "gross", "revolting", "filthy", "awful"),
    "fear": ("afraid", "scared", "terrified", "fear", "anxious", "worried"),
    "joy": ("happy", "joy", "glad", "delighted", "excited", "love", "great"),
    "sadness": ("sad", "unhappy", "miserable", "depressed", "lonely", "cry"),
}


def score_text(text):
    """Return deterministic pseudo-scores derived from a small keyword lexicon."""
    lowered = text.lower()
    raw = {
        emotion: sum(lowered.count(word) for word in words)
        for emotion, words in LEXICON.items()
    }
    total = sum(raw.values())
    if total == 0:
        return {emotion: 0.2 for emotion in LEXICON}
    return {emotion: round(1.0 if count == max(raw.values()) and count else
                           count / (total * 2), 4)
            for emotion, count in raw.items()}


class Handler(BaseHTTPRequestHandler):
    """Minimal Watson EmotionPredict-compatible handler."""

    def do_POST(self):  # noqa: N802 - http.server API
        """Validate the Watson header and answer with an emotion prediction."""
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        text = body.get("raw_document", {}).get("text", "")

        if not self.headers.get("grpc-metadata-mm-model-id"):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "missing model id"}')
            return

        payload = {"emotionPredictions": [{"emotion": score_text(text)}]}
        encoded = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *args):  # noqa: D102 - silence default logging
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9099
    print(f"Watson-compatible STUB (not IBM Watson) listening on port {port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
