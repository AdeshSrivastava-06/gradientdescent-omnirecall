# OmniRecall — Your Local Screen Memory

**Team GradientDescent | OSDHack 2026 — On Device AI**
#Demo video link- https://drive.google.com/file/d/161nhjFwpe22LuZrjpc7oZaqRKXP-9TDA/view?usp=sharing

A fully offline, privacy-first desktop app that lets you semantically search everything you've seen on your screen. No cloud, no APIs, no data leaving your machine.

---

## What It Does

Knowledge workers constantly lose track of transient information — a message that scrolled past, a code snippet they deleted, a recipe they glanced at. OmniRecall silently captures your screen locally, extracts the text with OCR, and lets you ask vague, natural questions later — like "what was that recipe with the mushroom" — and get back the answer plus the actual screenshot as proof.

Everything — capture, text extraction, embeddings, and answer generation — runs **entirely on your device**. Nothing is ever sent to the internet.

---

## How It Works (Simple Flow)

1. A background process takes a screenshot periodically, only when the screen has meaningfully changed
2. Local OCR (Tesseract) extracts the text
3. The text is embedded locally (Ollama + nomic-embed-text) and stored in a local SQLite database
4. When you ask a question, your query is embedded the same way and compared against stored memories using cosine similarity
5. The best-matching memories are passed to a local LLM (Llama 3.2 3B via Ollama), which answers grounded strictly in what was actually captured
6. The answer, confidence score, and matching screenshot are shown in a simple local web UI

---

## Features

- Offline OCR-based screen capture with smart deduplication (skips near-identical frames)
- Local semantic search over your own screen history
- Local LLM answers, grounded only in retrieved context (tested to avoid fabricating details)
- App/window name tagging — know which app a memory came from
- Time-based query filtering — "today," "yesterday," "this morning," "last hour"
- User-controlled privacy blocklist — toggle which apps are never captured (e.g. banking, password managers), fully editable, not hardcoded
- Automatic storage management — screenshots older than 3 hours are archived as lightweight text records and the image file is deleted, keeping disk usage bounded
- Time-travel viewer — browse the last 3 hours of captured screenshots chronologically
- On-demand daily summary — a local LLM-generated recap of what you did today

---

## Tech Stack

| Component | Tool |
|---|---|
| Screenshot capture | `mss` |
| Change detection | `imagehash` |
| OCR | Tesseract (via `pytesseract`) |
| Embeddings | `nomic-embed-text` (via Ollama) |
| Answer generation | `llama3.2:3b` (via Ollama) |
| Active window detection | `pygetwindow` |
| Storage | SQLite (built into Python) |
| Vector search | NumPy cosine similarity (no external vector DB) |
| UI | Streamlit |

No Node.js, no Docker, no cloud APIs. Pure Python + Ollama.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- Tesseract OCR engine installed — [Windows installer here](https://github.com/UB-Mannheim/tesseract/wiki)

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull required local models
```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

### 4. Set your Tesseract path
Open `capture_daemon.py` and confirm this line matches your install location:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 5. Run the background capture daemon
```bash
python capture_daemon.py
```
Leave this running in its own terminal window while you use your computer normally.

### 6. Run the app
In a **separate** terminal:
```bash
streamlit run app.py
```
This opens a local browser tab (`localhost:8501`) — nothing here touches the internet.

---

## Sample Usage

**Input (typed in search box):** `what was that recipe with the mushroom`

**Expected output:**
```
SUMMARY: You looked at a chocolate mug cake recipe involving mushrooms.
DETAILS:
- Mixed flour, cocoa powder, sugar, milk in a mug
- Microwaved for 90 seconds
- Topped with chopped mushrooms and honey glaze
SOURCE: [timestamp] captured while browsing
```
Below the answer: the best-matching screenshot with a confidence percentage, plus an option to view further matches.

**Input:** `what did I do this morning`
→ Filters search to only this morning's captures before running semantic search, then answers the same way.

---

## Privacy Controls

Go to the **Settings** tab in the app to:
- Toggle which apps are excluded from capture (pre-populated with common sensitive apps: banking, password managers, incognito browsers — all editable)
- Add your own custom app names to block

Blocked apps are **never** screenshotted, OCR'd, or stored — the skip happens before any capture occurs.

---

## Known Limitations

- OCR accuracy drops on small, cramped UI text (e.g. sidebar lists) and stylized/decorative text embedded in images (e.g. song lyric overlays on thumbnails) — normal application text, documents, code, and chat content are captured reliably
- Search quality depends on OCR quality; garbled text produces weaker matches
- This is a single-user, single-device tool by design — no sync, no accounts, no cloud backup

---

## License
MIT — see LICENSE file.
