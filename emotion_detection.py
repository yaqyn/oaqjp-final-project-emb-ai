"""Compatibility module for the course's root-level import style.

The graded activity runs ``from emotion_detection import emotion_detector``
from the project root, while the packaged implementation lives in
``EmotionDetection/emotion_detection.py``. This shim keeps both import paths
working without duplicating logic.
"""

from EmotionDetection.emotion_detection import emotion_detector

__all__ = ["emotion_detector"]
