"""
app.py — The Interactive Shell

Two tabs:
  Tab 1 "Code Mentor"    — the core PS3 deliverable (adaptive explainer + bugs + docs)
  Tab 2 "Rosetta Stone"  — stretch goal: same logic, two languages, side by side

gr.State holds a per-tab session_id, which becomes the LangGraph thread_id in
agent.py — this is the mechanism that makes conversation memory work per user.
"""

import os
import sys
import uuid
import gradio as gr

from safe_call import safe_call
from agent import analyze_code

# ---- Startup guard: fail loudly and immediately if the key is missing,
# rather than failing confusingly on the first click. ----
if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY is not set. Add it to your .env file.")
    sys.exit(1)


def _bugs_to_rows(bugs: list) -> list:
    """Convert the JSON bugs list into rows for gr.Dataframe: [[issue, fix], ...]."""
    if not bugs:
        return [["No bugs found.", ""]]
    return [[b.get("issue", ""), b.get("fix", "")] for b in bugs]


@safe_call
def handle_submit(code_input: str, level: str, traceback_input: str, session_id: str, progress=gr.Progress()):
    if not code_input or not code_input.strip():
        # Empty-input validation — required by PS3 test scenario #4 equivalent.
        empty_result = {
            "breakdown": "Please paste a code snippet before submitting.",
            "analogy": "", "bugs": [], "doc_findings": None, "optimized_snippet": "",
        }
        return empty_result, "No request sent — input was empty."

    progress(0.1, desc="Preparing request…")

    # Fold an optional traceback into the same user message so the agent can
    # use it as extra context, without needing a separate tool or code path.
    user_message = code_input
    if traceback_input and traceback_input.strip():
        user_message += f"\n\n--- User-provided traceback/error log ---\n{traceback_input}"

    progress(0.4, desc="Agent is reasoning (may call tools)…")
    parsed, trace = analyze_code(user_message, level, session_id)
    progress(1.0, desc="Done.")
    return parsed, trace


@safe_call
def handle_translate(source_code: str, source_lang: str, target_lang: str, progress=gr.Progress()):
    """Rosetta Stone tab: translate a snippet and explain the idiomatic differences.
    Deliberately a separate, simpler direct LLM call (not the ReAct agent) —
    this task needs no tools, just one well-structured prompt."""
    if not source_code or not source_code.strip():
        return "", "Please paste some code first."

    from langchain_groq import ChatGroq
    progress(0.2, desc="Translating…")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

    prompt = f"""Translate the following {source_lang} code into idiomatic {target_lang}.
Respond with ONLY valid JSON, no markdown fences, matching:
{{"translated_code": "string", "differences": "Markdown string explaining the key
idiomatic/architectural differences between the two versions."}}

Source code ({source_lang}):
{source_code}"""

    progress(0.6, desc="Waiting for model…")
    response = llm.invoke(prompt)

    import json
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    result = json.loads(text)
    progress(1.0, desc="Done.")
    return result.get("translated_code", ""), result.get("differences", "")


with gr.Blocks(title="Code Mentor — Adaptive AI Code Explainer") as demo:
    session_id = gr.State(value=lambda: str(uuid.uuid4()))

    gr.Markdown("# 🧑‍🏫 Code Mentor\n*Adaptive code explanations, bug fixes, and real documentation lookups.*")

    with gr.Tabs():
        # ---------------- TAB 1: Code Mentor ----------------
        with gr.Tab("💡 Code Mentor"):
            with gr.Row():
                with gr.Column(scale=1):
                    code_input = gr.Textbox(
                        label="Paste your code",
                        lines=14,
                        placeholder="Paste a Python, JS, Java, or C++ snippet here…",
                    )
                    traceback_input = gr.Textbox(
                        label="Optional: paste an error traceback",
                        lines=4,
                        placeholder="Paste a raw error log if you have one (optional)…",
                    )
                    level = gr.Dropdown(
                        choices=["Beginner", "Intermediate", "Expert"],
                        value="Beginner",
                        label="Explanation level",
                    )
                    submit_btn = gr.Button("Analyze Code", variant="primary")

                with gr.Column(scale=2):
                    with gr.Accordion("Analogy", open=True):
                        analogy_out = gr.Markdown()
                    with gr.Accordion("Line-by-Line Breakdown", open=True):
                        breakdown_out = gr.Markdown()
                    with gr.Accordion("Bugs & Fixes", open=True):
                        bugs_out = gr.Dataframe(headers=["Issue", "Fix"], wrap=True)
                    with gr.Accordion("Documentation Findings", open=False):
                        docs_out = gr.Markdown()
                    with gr.Accordion("Optimized Code", open=True):
                        # gr.Code renders with a built-in copy button — this satisfies
                        # the "one-click Copy Code" requirement with zero extra wiring.
                        code_out = gr.Code(language="python")
                    with gr.Accordion("🔍 Agent Reasoning Trace", open=False):
                        trace_out = gr.Textbox(interactive=False, lines=6)

            def _submit_and_unpack(code_input, level, traceback_input, session_id):
                parsed, trace = handle_submit(code_input, level, traceback_input, session_id)
                return (
                    parsed.get("analogy", ""),
                    parsed.get("breakdown", ""),
                    _bugs_to_rows(parsed.get("bugs", [])),
                    parsed.get("doc_findings") or "No documentation lookup was needed.",
                    parsed.get("optimized_snippet", ""),
                    trace,
                )

            submit_btn.click(
                _submit_and_unpack,
                inputs=[code_input, level, traceback_input, session_id],
                outputs=[analogy_out, breakdown_out, bugs_out, docs_out, code_out, trace_out],
            )

        # ---------------- TAB 2: Rosetta Stone (stretch goal) ----------------
        with gr.Tab("🌐 Rosetta Stone"):
            gr.Markdown("Paste code in one language, translate it to another, and see the idiomatic differences.")
            with gr.Row():
                source_lang = gr.Dropdown(
                    choices=["Python", "JavaScript", "Java", "C++"], value="Python", label="From"
                )
                target_lang = gr.Dropdown(
                    choices=["Python", "JavaScript", "Java", "C++"], value="JavaScript", label="To"
                )
            with gr.Row():
                source_code = gr.Textbox(label="Source code", lines=12)
                translated_code = gr.Code(label="Translated code", language="javascript")
            differences_out = gr.Markdown(label="Architectural differences")
            translate_btn = gr.Button("Translate", variant="primary")

            translate_btn.click(
                handle_translate,
                inputs=[source_code, source_lang, target_lang],
                outputs=[translated_code, differences_out],
            )

if __name__ == "__main__":
    demo.launch()
