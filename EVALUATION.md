# Evaluation — OmniRecall

## Retrieval Accuracy Test

**Method:** 5 synthetic "memories" covering distinct topics (a recipe, a code snippet, meeting notes, a video title, a bug report) were stored with their embeddings. 5 deliberately vague natural-language questions were then asked, each designed to match exactly one memory. The top-1 retrieved result was checked against the expected correct memory.

**Result: 5 / 5 correct retrievals.**

| Question | Expected Match | Retrieved Match | Similarity Score | Correct? |
|---|---|---|---|---|
| "what was that recipe with the weird mushroom" | Recipe entry | Recipe entry | 0.578 | Yes |
| "find that code I deleted about factorial" | Code entry | Code entry | 0.540 | Yes |
| "what did we decide about the budget" | Meeting notes | Meeting notes | 0.593 | Yes |
| "that hindi song I was watching" | Video entry | Video entry | 0.721 | Yes |
| "why is my product list broken" | Bug report | Bug report | 0.634 | Yes |

## Answer Grounding / Hallucination Check

During the same test, two of the five LLM-generated answers correctly stated that the retrieved information was insufficient to fully answer the question, rather than fabricating plausible-sounding details. This was treated as a pass, not a failure — the desired behavior is honest uncertainty over confident fabrication.

An earlier, separate test (during system prompt development) explicitly caught the model inventing a vital sign (temperature) and a medicine that were never mentioned in a source transcript, under a permissive prompt. Adding explicit "only use what is stated, say 'not mentioned' otherwise" instructions to the prompt eliminated this behavior in subsequent tests. The same grounding discipline is applied in OmniRecall's answer prompt.

## OCR Accuracy — Real-World Screenshots

**Method:** Manual visual comparison between original screenshots and Tesseract's extracted text output, across varied real content types.

| Content type | Result |
|---|---|
| Standard application text / long-form paragraphs | Strong — near word-for-word accurate |
| Video titles, channel names, UI metadata (e.g. YouTube page) | Strong — accurately captured |
| Code editor / file explorer (dense, small UI text) | Weak — fragments garbled, mixed with sidebar noise |
| Stylized decorative text embedded in images (e.g. song lyric overlay on a thumbnail) | Poor — output unreadable, as expected for OCR on artistic fonts over busy backgrounds |
| Small cramped sidebar lists (e.g. chat history panel) | Weak — several entries misread |

## Known Failure Cases

1. **Decorative/stylized image text** (thumbnails, artistic overlays) — not reliably extractable by any general-purpose OCR engine, not a defect specific to this implementation.
2. **Dense small UI elements** (sidebars, tightly packed lists) — lower accuracy than standard document/paragraph text.
3. **Close-scoring ambiguous queries** — when multiple stored memories are topically similar, confidence scores can cluster closely (observed similarity scores as close as ~0.46–0.58 across unrelated top candidates in one real test), which can make the top-1 result less certain. The UI surfaces a low-confidence warning below a 0.4 similarity threshold and offers additional matches to mitigate this.

## Baseline Comparison

No formal baseline benchmark was run against commercial tools (e.g. Windows Recall, Rewind.ai) due to their cloud dependency and closed-source nature, which makes direct like-for-like comparison impractical within the hackathon timeframe. The qualitative differentiator is architectural: OmniRecall's OCR, embeddings, and generation all run on-device, whereas comparable commercial tools are cloud-adjacent or closed-source.
