"""Flask web application for the Emotion Detector final project."""

from flask import Flask, jsonify, render_template, request

from EmotionDetection.emotion_detection import MAX_TEXT_LENGTH, MODEL_ID, emotion_detector

app = Flask(__name__)

INVALID_TEXT_MESSAGE = "Invalid text! Please try again!"
SERVICE_ERROR_MESSAGE = (
    "The emotion detection service is temporarily unavailable. "
    "Please try again later."
)
TEXT_TOO_LONG_MESSAGE = "Text is too long. Please use 5,000 characters or fewer."


@app.route("/")
def render_index_page():
    """Render the course-provided Emotion Detection web page."""
    return render_template("index.html")


@app.route("/health")
def health_check():
    """Report local application readiness without calling Watson."""
    return jsonify(
        status="ok",
        model_id=MODEL_ID,
        max_text_length=MAX_TEXT_LENGTH,
    )


@app.route("/emotionDetector")
def run_emotion_detector():
    """Analyse the ``textToAnalyze`` query parameter and format the response."""
    text_to_analyze = request.args.get("textToAnalyze", "")

    if not text_to_analyze.strip():
        return INVALID_TEXT_MESSAGE

    try:
        result = emotion_detector(text_to_analyze)
    except ValueError:
        return TEXT_TOO_LONG_MESSAGE, 413
    except RuntimeError:
        return SERVICE_ERROR_MESSAGE, 503

    if result["dominant_emotion"] is None:
        return INVALID_TEXT_MESSAGE

    return (
        "For the given statement, the system response is "
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']}, "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
