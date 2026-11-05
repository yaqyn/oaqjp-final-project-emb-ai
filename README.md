# Final Project - Emotion Detector (IBM Skills Network)

This repository contains the **Final Project** for the IBM Skills Network /
Coursera course *Developing AI Applications with Python and Flask*.

The application sends text to the IBM Watson NLP `EmotionPredict` service and
reports five emotion scores (`anger`, `disgust`, `fear`, `joy`, `sadness`)
together with the `dominant_emotion`.

## Project structure

```
.
├── EmotionDetection/
│   ├── __init__.py            # exposes emotion_detector
│   └── emotion_detection.py   # Watson NLP integration
├── emotion_detection.py       # root-level compatibility shim
├── server.py                  # Flask application
├── test_emotion_detection.py  # unittest suite
├── templates/index.html       # course-provided frontend
├── static/mywebscript.js      # course-provided frontend logic
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the web application

```bash
python3 server.py
```

Open <http://localhost:5000>, enter a sentence such as
`I am very happy today` and click **Run Sentiment Analysis**.

The `/emotionDetector` endpoint accepts the `textToAnalyze` query parameter:

```text
http://localhost:5000/emotionDetector?textToAnalyze=I%20am%20very%20happy%20today
```

Blank input returns `Invalid text! Please try again!`. A Watson outage returns a
service error (HTTP 503) instead of being reported as invalid input.

## Use the detector directly

```bash
python3 -c "from emotion_detection import emotion_detector; print(emotion_detector('I am really mad about this'))"
```

```python
{'anger': 0.99, 'disgust': 0.01, 'fear': 0.01, 'joy': 0.00, 'sadness': 0.01, 'dominant_emotion': 'anger'}
```

## Tests

```bash
python3 test_emotion_detection.py
python3 -m unittest -v
```

The deterministic tests mock `requests.post`. To run the optional integration
test against the real Watson service (requires access to the IBM Skills Network
lab network):

```bash
RUN_LIVE_TESTS=1 python3 -m unittest -v
```

## Static analysis

```bash
python3 -m pylint server.py
```

## Service endpoint

```text
POST https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict
grpc-metadata-mm-model-id: emotion_aggregated-workflow_lang_en_stock
```

The endpoint may be overridden with the `WATSON_EMOTION_URL` environment
variable, which is useful for offline UI testing against a local Watson-
compatible service.
