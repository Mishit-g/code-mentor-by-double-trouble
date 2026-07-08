# Code Mentor 🧑‍🏫

**Adaptive AI code explainer that meets you at your level — and checks its own claims against real documentation.**

Built for **MSTC GenAI Summer of Code — Hackathon 2026**, Problem Statement **PS3: CodeMentor (Adaptive Code Explainer)**.

Paste any Python, JavaScript, Java, or C++ snippet, pick a level — Beginner, Intermediate, or Expert — and get a line-by-line breakdown, a level-appropriate analogy, concrete bug fixes, a Big-O complexity chart, and a documentation lookup the agent actually performed, not guessed. Ask a natural follow-up ("what if I removed line 4?") and it remembers the original snippet. There's also a **Rosetta Stone** tab that translates the same logic into another language and explains what changed and why.

---

## ✨ Features

| Area | What it does |
|---|---|
| **Three genuine personas** | Beginner, Intermediate, and Expert each run a *structurally different* system prompt (own vocabulary rules, own forbidden moves, own analogy style) — not one prompt with an adjective swapped in. See [`prompts.py`](./prompts.py). |
| **Agentic doc verification** | A LangGraph `create_react_agent` decides, per snippet, whether to call `library_docs_search` (DuckDuckGo) to verify an unfamiliar library/API, or `github_fetcher` to pull code straight from a GitHub blob URL. |
| **Structured JSON contract** | Every response — including follow-ups — is forced into one strict schema (`breakdown`, `analogy`, `bugs[]`, `doc_findings`, `optimized_snippet`, `time_complexity`), so the UI can reliably route model output to the right panel. |
| **Conversation memory** | `MemorySaver` keyed by a per-browser-tab `session_id` (LangGraph `thread_id`), so follow-up questions reuse the original snippet without the user re-pasting it. |
| **Big-O visualization** | A Plotly chart plots the model's declared time complexity against the standard O(1)–O(n²) reference curves, live, per analysis. |
| **Rosetta Stone tab** | Translates a snippet into idiomatic code in another language (Python/JS/Java/C++) and explains the architectural differences and paradigm-shift caveats. |
| **Reasoning trace** | Every tool call the agent makes — name, arguments — is logged from real `agent.stream()` output and shown in a collapsible "Agent Reasoning Trace" accordion. Nothing is fabricated. |
| **Judge-proof error handling** | A single `@safe_call` decorator wraps every Gradio-facing handler. Recursion-limit hits, malformed JSON, Groq rate limits, and any unexpected exception all degrade to a short, readable message — a judge should never see a raw Python traceback. |
| **Custom theme** | A bespoke "Margin Note" visual identity (Notebook/Chalkboard light-dark modes, Fraunces + Inter + JetBrains Mono type system, hand-drawn highlighter underline) — see [`theme.py`](./theme.py). |

---

## 🏗️ Architecture

```
User (Gradio Blocks UI)
        │
        ▼
   app.py  ──────────────► theme.py (visual identity, CSS, light/dark toggle)
        │
        │  wraps every handler in
        ▼
  safe_call.py  (never let a raw traceback reach the UI)
        │
        ▼
   agent.py  ──► prompts.py     (persona system prompts, JSON schema contract)
        │
        ▼
  LangGraph create_react_agent
  (Groq · llama-3.3-70b-versatile · temperature=0.2)
        │
        ├──► tools.py: github_fetcher      (pull code from a github.com URL)
        └──► tools.py: library_docs_search (DuckDuckGo doc verification)
        │
        ▼
  MemorySaver, keyed by session_id → thread_id
  (gives each browser tab its own follow-up memory)
```

**Why a ReAct agent and not a single prompt?** The model needs to *decide*, per snippet, whether it actually needs to verify a library call against real docs — calling a tool on every request would be slow and often pointless; never calling one would mean "documentation findings" are just hallucinated. `create_react_agent` lets the LLM make that call itself, and the trace panel proves it.

**Why is the persona injected per-call instead of baked into the agent at creation time?** The agent instance (and its memory) is created once and reused across all requests, but the user can pick a different level on every submit while still wanting the same conversation thread. So `agent.py` builds one `SystemMessage` per call from `PERSONAS[level]` and streams it in fresh, while `thread_id` keeps continuity.

---

## 🛠️ Tech Stack

- **LangGraph** (`create_react_agent`, `MemorySaver`) — agent orchestration + memory
- **LangChain** (`@tool`, `DuckDuckGoSearchRun`) — tool definitions
- **Groq API** (`llama-3.3-70b-versatile`) — inference
- **Gradio Blocks** — UI, with a custom `gr.themes.Base` theme and hand-rolled CSS
- **Plotly** — live Big-O complexity chart
- **python-dotenv** — local secrets

---

## 🚀 Setup

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then open .env and add your real GROQ_API_KEY

python app.py
```

The app will refuse to start with a clear message if `GROQ_API_KEY` is missing (see the startup guard in `app.py`) — no confusing runtime crash three clicks in.

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key. Get one free at [console.groq.com](https://console.groq.com). |

---

## 📁 Project Structure

```
.
├── app.py            # Gradio Blocks UI, event wiring, Plotly chart generation
├── agent.py           # LangGraph agent setup, memory, persona injection, JSON extraction
├── tools.py           # @tool-decorated functions the agent can call
├── prompts.py          # SYSTEM_BASE JSON contract + 3 distinct persona prompts
├── safe_call.py        # Decorator: catches every failure mode, returns a clean message
├── theme.py            # Custom Gradio theme, CSS, light/dark toggle, fonts
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🧪 Test Scenarios

| # | Scenario | Expected result |
|---|---|---|
| 1 | Paste the same 15-line Python snippet at all three levels | Beginner explains chronologically with plain-English definitions and a physical-object analogy; Intermediate skips syntax and calls out idiomatic vs. non-idiomatic patterns; Expert skips straight to Big-O/Big-Ω and architecture — no persona ever just reads "more advanced" versions of the same text. |
| 2 | Paste a snippet importing a less-common call (e.g. `asyncio.gather`) | The agent calls `library_docs_search`, and the reasoning trace shows the real tool call; `doc_findings` reflects an actual search result, not a guess. |
| 3 | Paste a snippet with an intentional off-by-one bug | `bugs[]` catches it with a specific, concrete fix — not a generic "add error handling." |
| 4 | Ask a follow-up like *"what would happen if I removed line 4?"* | The agent answers using the original snippet from `MemorySaver`/`thread_id` — no re-paste needed. |
| 5 | Paste a `github.com/.../blob/...` URL as part of the prompt | `github_fetcher` converts it to the raw content URL and pulls real code, rather than the model hallucinating file contents. |
| 6 | Submit an empty code box | A clear validation message appears (`handle_submit`'s empty-input guard) — no API call, no traceback. |
| 7 | Force a recursion-limit / rate-limit / malformed-JSON failure | `safe_call` intercepts each one and returns a short, human-readable error string — the UI never shows a raw stack trace. |
| 8 | Use the **Rosetta Stone** tab to translate a Python snippet to JavaScript | Translated code renders with correct formatting (real newlines, not one collapsed line) plus a bulleted list of architectural differences. |

---

## ⚠️ Known Limitations

- `library_docs_search` depends on DuckDuckGo's unauthenticated search endpoint, which can rate-limit or degrade under rapid repeated calls during a live judging session — `safe_call` catches this gracefully, but results may occasionally be thinner than expected.
- `github_fetcher` only supports public, unauthenticated GitHub blob URLs (no private repos, no GitLab/Bitbucket).
- Conversation memory (`MemorySaver`) is in-process and per-`session_id`; it does not persist across app restarts or scale across multiple server workers.
- The Rosetta Stone tab calls the LLM directly (no agent/tools), so it does not verify translated syntax against real documentation the way the main tab does.
- `recursion_limit=10` means an unusually convoluted multi-tool chain of reasoning can hit the ceiling on rare inputs; `safe_call` reports this cleanly rather than hanging.

---

## 🎥 Live Demo & Video

- **Live demo:** `<add your Hugging Face Spaces / Gradio share link here>`
- **Demo video (5 min):** `<add your video link here>`

---

## 🙏 Acknowledgements

Built during the **MSTC GenAI Summer of Code — Hackathon 2026**, using the six weeks of prompt-chaining, agents, and structured-output techniques from the learning phase, for Problem Statement PS3 — CodeMentor.
