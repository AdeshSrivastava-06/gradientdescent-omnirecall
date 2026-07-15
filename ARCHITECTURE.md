# System Architecture — OmniRecall

## Overview Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                     USER'S LAPTOP (fully offline)              │
│                                                                 │
│   ┌────────────────────┐                                       │
│   │  capture_daemon.py  │  (background process, always running)│
│   │                     │                                      │
│   │  1. Get active window name (pygetwindow)                   │
│   │  2. Check privacy blocklist (SQLite settings table)        │
│   │     → if blocked, skip entirely                            │
│   │  3. Screenshot (mss)                                       │
│   │  4. Compare to last screenshot hash (imagehash)             │
│   │     → if unchanged, skip                                   │
│   │  5. OCR text extraction (Tesseract / pytesseract)           │
│   │  6. Clean OCR text (regex noise removal)                   │
│   │  7. Generate embedding (Ollama: nomic-embed-text)           │
│   │  8. Save to SQLite: timestamp, app, text, path, embedding   │
│   │  9. Every ~5 min: archive screenshots older than 3h         │
│   │     → delete PNG, keep JSON text record in DB               │
│   └──────────┬──────────┘                                      │
│              │ writes to                                       │
│              ▼                                                 │
│   ┌────────────────────┐                                       │
│   │   omnirecall.db     │  (SQLite — captures + app_settings)  │
│   └──────────┬──────────┘                                      │
│              │ read by                                         │
│              ▼                                                 │
│   ┌────────────────────┐                                       │
│   │      app.py         │  (Streamlit UI, opened on demand)    │
│   │                     │                                      │
│   │  Search tab:                                                │
│   │   query → embed (Ollama) → detect time keywords             │
│   │   → filter candidates → cosine similarity → top matches     │
│   │   → pass to LLM (llama3.2:3b) → structured answer           │
│   │                                                              │
│   │  Time Travel tab:                                            │
│   │   slider over last 3h of captures, chronological browse      │
│   │                                                              │
│   │  Daily Summary tab:                                          │
│   │   on-demand: all of today's captures → LLM summary           │
│   │                                                              │
│   │  Settings tab:                                                │
│   │   toggle blocked apps, add custom entries                     │
│   └────────────────────┘                                       │
│                                                                 │
└───────────────────────────────────────────────────────────────┘

  NOTHING in this diagram makes a network call. No component
  requires or uses internet access for its core function.
```

---

## Data Flow — Capture Path

1. `get_active_app_name()` reads the OS-level focused window title
2. `is_blocked()` checks that name against the `app_settings` table
3. If not blocked: screenshot → hash comparison → (if changed) OCR → clean → embed → store
4. Every N cycles, `run_storage_cleanup()` finds captures older than 3 hours that still have a screenshot file, deletes the PNG, and writes a compact JSON record (`{timestamp, app_name, text}`) into the `archived_json` column instead

## Data Flow — Search Path

1. User query typed in Streamlit
2. `detect_time_range()` checks for keywords ("today", "yesterday", "this morning", "last hour")
3. If found: only captures in that timestamp range are considered; otherwise all captures are considered
4. Query is embedded (same model as capture-time embeddings, for consistency)
5. Cosine similarity is computed between the query embedding and each candidate's stored embedding, in-memory with NumPy
6. Top 3 matches are passed as context to the LLM with a strict "answer only from this context" prompt
7. LLM returns a structured SUMMARY / DETAILS / SOURCE answer
8. UI displays the answer, the best match's confidence and screenshot prominently, with the remaining matches available in a collapsed section

---

## Local vs Cloud Components

| Component | Runs where |
|---|---|
| Screenshot capture | 100% local |
| OCR | 100% local (Tesseract, no cloud OCR API) |
| Embeddings | 100% local (Ollama) |
| Answer generation | 100% local (Ollama) |
| Storage | 100% local (SQLite file on disk) |
| UI | 100% local (Streamlit serves to `localhost` only) |

No component in this system calls an external API for its core AI functionality, in compliance with the OSDHack On-Device AI theme.

---

## Key Design Decisions

- **Screenshots over accessibility-API hooking:** Real-time accessibility API text extraction across every application is inconsistent (many apps block or poorly expose it) and was assessed as too high-risk for the build window. Periodic screenshot + OCR gives comparable practical coverage with far lower engineering risk.
- **NumPy cosine similarity over a vector database (e.g. ChromaDB):** At the scale of a single user's screen history (hundreds to low thousands of entries), a dedicated vector database adds dependency weight without a measurable performance benefit. A vector DB would matter at a much larger scale than this use case reaches.
- **Ollama for both embeddings and generation:** Avoids installing a second ML runtime (e.g. PyTorch + sentence-transformers) alongside Ollama, reducing disk footprint and the number of moving parts that can fail independently.
- **Privacy blocklist is user-editable, not hardcoded:** Initial design used a fixed list of sensitive app names; this was changed so the user has full control over what is/isn't ever captured, since privacy decisions should not be made unilaterally by the tool.
- **3-hour screenshot retention, then text-only archive:** Balances demo/proof value (recent screenshots stay visible as evidence) against unbounded local disk growth from continuous PNG capture.
