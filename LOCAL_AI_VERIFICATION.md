# Local AI Verification — OmniRecall

## What Runs Fully On-Device

Every AI component in this system runs locally, with no network dependency:

- **Screen capture** — local screenshot API (`mss`), no external service
- **OCR / text extraction** — Tesseract runs as a local binary, no cloud OCR API (e.g. no Google Vision, no AWS Textract)
- **Embedding generation** — `nomic-embed-text` served by a locally-running Ollama instance
- **Answer generation** — `llama3.2:3b` served by the same local Ollama instance
- **Semantic search** — cosine similarity computed in-process with NumPy, no external vector database service
- **Storage** — SQLite, a local file on disk

## What Requires Internet

**Nothing, for core functionality.** Internet is only used for:
- The one-time initial download of Python packages (`pip install`) and Ollama models (`ollama pull`) during setup
- No feature of the running application makes a network call

## Does Any User Data Leave the Device?

**No.** Captured screenshots, extracted text, embeddings, and generated answers are all stored and processed exclusively on the local machine, in a local SQLite database and a local screenshots folder. No API calls are made to any external service during normal operation.

## Verification Method

This was tested manually by disabling WiFi and mobile data entirely, then running the full pipeline end-to-end (capture → OCR → embed → search → answer) and confirming it completed successfully with no errors or hanging network requests.

## Compliance with OSDHack 2026 Rules

Per the hackathon rules: *"Cloud services are allowed for support features like hosting, authentication, storage, databases, or deployment. The main AI feature, however, should run on-device, locally, in-browser, on edge, or on embedded hardware."*

OmniRecall's core AI feature — screen understanding and semantic recall — runs entirely on-device. No cloud service of any kind (support or core) is used in the current build.
