"""Unit tests for the Watson NLP emotion detection application.

The deterministic tests mock ``requests.post`` so they verify the parsing and
formatting logic without network access. The optional live test performs a real
call to the IBM Watson NLP endpoint and only runs when ``RUN_LIVE_TESTS=1``.
"""

import os
import unittest
from unittest.mock import patch

from EmotionDetection.emotion_detection import emotion_detector
from server import app

MOCKED_EMOTIONS = {
    "anger": 0.02,
    "disgust": 0.01,
    "fear": 0.03,
    "joy": 0.90,
    "sadness": 0.04,
}


def watson_payload(overrides=None):
    """Return a Watson-shaped emotion prediction payload."""
    emotions = dict(MOCKED_EMOTIONS)
    if overrides:
        emotions.update(overrides)
    return {"emotionPredictions": [{"emotion": emotions}]}


class MockResponse:
    """Minimal stand-in for a ``requests.Response``."""

    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        """Return the decoded JSON body."""
        return self._payload


class TestEmotionDetector(unittest.TestCase):
    """Tests for the five dominant emotions, blank input and HTTP 400."""

    def assert_dominant(self, text, expected_emotion, overrides=None):
        """Assert that ``text`` resolves to ``expected_emotion``."""
        emotions = dict(MOCKED_EMOTIONS)
        if overrides:
            emotions.update(overrides)

        with patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=MockResponse(200, watson_payload(overrides)),
        ):
            result = emotion_detector(text)

        self.assertEqual(result["dominant_emotion"], expected_emotion)
        for emotion in ("anger", "disgust", "fear", "joy", "sadness"):
            self.assertIsInstance(result[emotion], float)
        self.assertEqual(
            result, {**emotions, "dominant_emotion": expected_emotion}
        )

    def test_joy(self):
        """Joy is dominant for a happy statement."""
        self.assert_dominant("I am very happy today", "joy", {"joy": 0.95})

    def test_anger(self):
        """Anger is dominant for an angry statement."""
        self.assert_dominant("I am really mad about this", "anger", {"anger": 0.97})

    def test_disgust(self):
        """Disgust is dominant for a disgusted statement."""
        self.assert_dominant("This smells revolting", "disgust", {"disgust": 0.93})

    def test_sadness(self):
        """Sadness is dominant for a sad statement."""
        self.assert_dominant("I am so sad about the news", "sadness", {"sadness": 0.92})

    def test_fear(self):
        """Fear is dominant for a frightened statement."""
        self.assert_dominant("I am terrified of the dark", "fear", {"fear": 0.94})

    def test_blank_input(self):
        """Blank input returns six ``None`` values without calling Watson."""
        with patch(
            "EmotionDetection.emotion_detection.requests.post"
        ) as mocked_post:
            for text in ("", "   ", "\n\t"):
                result = emotion_detector(text)
                self.assertEqual(
                    result,
                    {
                        "anger": None,
                        "disgust": None,
                        "fear": None,
                        "joy": None,
                        "sadness": None,
                        "dominant_emotion": None,
                    },
                )
        mocked_post.assert_not_called()

    def test_http_400(self):
        """HTTP 400 from Watson returns six ``None`` values."""
        with patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=MockResponse(400),
        ):
            result = emotion_detector("some text")

        self.assertEqual(
            result,
            {
                "anger": None,
                "disgust": None,
                "fear": None,
                "joy": None,
                "sadness": None,
                "dominant_emotion": None,
            },
        )

    def test_oversized_input_is_rejected_before_watson(self):
        """Bound requests before they are sent to the remote service."""
        with patch("EmotionDetection.emotion_detection.requests.post") as mocked_post:
            with self.assertRaisesRegex(ValueError, "at most 5000"):
                emotion_detector("x" * 5001)
        mocked_post.assert_not_called()

    def test_web_endpoint_reports_oversized_input(self):
        """The HTTP route returns a specific payload-too-large response."""
        with app.test_client() as client:
            response = client.get("/emotionDetector", query_string={"textToAnalyze": "x" * 5001})
        self.assertEqual(response.status_code, 413)
        self.assertIn("5,000 characters or fewer", response.get_data(as_text=True))


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_TESTS") == "1",
    "Live Watson NLP test disabled; set RUN_LIVE_TESTS=1 to enable (requires lab network access).",
)
class TestLiveWatsonService(unittest.TestCase):
    """Optional integration test that calls the real Watson NLP endpoint."""

    def test_live_anger(self):
        """A real Watson call classifies an angry sentence as anger."""
        result = emotion_detector("I am really mad about this")
        self.assertEqual(result["dominant_emotion"], "anger")
        for emotion in ("anger", "disgust", "fear", "joy", "sadness"):
            self.assertIsInstance(result[emotion], float)


if __name__ == "__main__":
    unittest.main(verbosity=2)
