# Code Mentor — Adaptive AI Code Explainer

Adaptive code explainer that adjusts depth (Beginner / Intermediate / Expert),
identifies bugs with concrete fixes, and verifies library/API usage against
real documentation via an agent with a web-search tool.

## Architecture
- **LangGraph `create_react_agent`** — ReAct loop, routes to tools when needed
- **Tools**: `github_fetcher` (fetch code from a GitHub URL), `library_docs_search`
  (DuckDuckGo doc lookup)
- **Memory**: `MemorySaver`, keyed by a per-session `thread_id`, so follow-up
  questions reuse the original snippet
- **Gradio Blocks UI**: multi-accordion output panel + Rosetta Stone translation tab

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your real GROQ_API_KEY
python app.py
```

## Known limitations
- (fill in during testing — e.g. rate limits on DuckDuckGo after many rapid calls)

## Test scenarios run
- [ ] Same 15-line snippet at all 3 levels — meaningfully different outputs
- [ ] Snippet importing an uncommon library — real doc finding surfaced
- [ ] Snippet with an intentional off-by-one bug — caught with a specific fix
- [ ] Follow-up question ("what if I removed line 4?") — uses memory, no re-paste needed
