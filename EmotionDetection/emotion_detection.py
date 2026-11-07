"""Emotion detection using the IBM Watson NLP emotion prediction service.

The module exposes :func:`emotion_detector`, which sends a piece of text to the
Watson NLP ``EmotionPredict`` endpoint and returns the five emotion scores plus
the dominant emotion.
"""

import math
import os
from numbers import Real

import requests

DEFAULT_ENDPOINT = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)

# The endpoint can be overridden so the application can be exercised against a
# local Watson-compatible service when the IBM Skills Network lab is unreachable.
EMOTION_ENDPOINT = os.environ.get("WATSON_EMOTION_URL", DEFAULT_ENDPOINT)

MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"
REQUEST_TIMEOUT = 10
MAX_TEXT_LENGTH = 5000
EMOTION_KEYS = ("anger", "disgust", "fear", "joy", "sadness")


def _empty_result():
    """Build the canonical result dictionary whose values are all ``None``."""
    result = {emotion: None for emotion in EMOTION_KEYS}
    result["dominant_emotion"] = None
    return result


def _request_headers():
    """Return the headers required by the Watson NLP runtime."""
    return {
        "grpc-metadata-mm-model-id": MODEL_ID,
        "Content-Type": "application/json",
    }


def emotion_detector(text_to_analyze):
    """Detect emotions in ``text_to_analyze`` with Watson NLP.

    Args:
        text_to_analyze (str): Text whose emotions should be classified.

    Returns:
        dict: A dictionary with the keys ``anger``, ``disgust``, ``fear``,
        ``joy``, ``sadness`` and ``dominant_emotion``. All six values are
        ``None`` when the input is blank or Watson answers with HTTP 400.

    Raises:
        RuntimeError: If the Watson service cannot be reached or returns an
            unexpected response. This is a service-side failure and must not be
            reported to the user as invalid input.
    """
    if text_to_analyze is None or not str(text_to_analyze).strip():
        return _empty_result()
    if len(str(text_to_analyze)) > MAX_TEXT_LENGTH:
        raise ValueError(f"Text must contain at most {MAX_TEXT_LENGTH} characters.")

    payload = {"raw_document": {"text": str(text_to_analyze)}}

    try:
        response = requests.post(
            EMOTION_ENDPOINT,
            json=payload,
            headers=_request_headers(),
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "The emotion detection service could not be reached."
        ) from exc

    if response.status_code == 400:
        return _empty_result()

    if response.status_code != 200:
        raise RuntimeError(
            f"The emotion detection service returned HTTP {response.status_code}."
        )

    try:
        scores = response.json()["emotionPredictions"][0]["emotion"]
        result = {}
        for emotion in EMOTION_KEYS:
            score = scores[emotion]
            if (
                isinstance(score, bool)
                or not isinstance(score, Real)
                or not math.isfinite(score)
                or not 0 <= score <= 1
            ):
                raise ValueError(f"Invalid score for {emotion}.")
            result[emotion] = float(score)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "The emotion detection service returned an unexpected response."
        ) from exc

    result["dominant_emotion"] = max(
        EMOTION_KEYS, key=lambda emotion: result[emotion]
    )
    return result
