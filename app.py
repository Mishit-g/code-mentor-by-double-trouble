"""
app.py — The Interactive Shell (Now with Plotly Graphics!)
"""

import os
import sys
import uuid
import math
import json
import gradio as gr
import plotly.graph_objects as go

from safe_call import safe_call
from agent import analyze_code
from theme import CODEMENTOR_THEME, CUSTOM_CSS, HEAD_HTML, THEME_TOGGLE_JS

# ---- Startup guard ----
if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY is not set. Add it to your .env file.")
    sys.exit(1)


_LEVEL_ORDER = ["Beginner", "Intermediate", "Expert"]
_LANG_TO_CODE_LANG = {"Python": "python", "JavaScript": "javascript", "Java": "java", "C++": "cpp"}

# ---- Empty-state copy: an empty panel is an invitation to act, not a blank ----
_EMPTY_ANALOGY = "_Paste code on the left and click **Analyze Code** — a plain-language analogy will appear here._"
_EMPTY_BREAKDOWN = "_Your line-by-line walkthrough will appear here._"
_EMPTY_DOCS = "_No documentation lookup needed yet._"
_EMPTY_BUGS = [["No analysis yet.", ""]]


def _bugs_to_rows(bugs: list) -> list:
    if not bugs:
        return [["No bugs found.", ""]]
    return [[b.get("issue", ""), b.get("fix", "")] for b in bugs]


def _level_meter_html(level: str) -> str:
    """Renders the 3-dot level meter — a real ordinal sequence
    (Beginner < Intermediate < Expert), tracking the dropdown live."""
    idx = _LEVEL_ORDER.index(level)
    dots = "".join(
        f'<span class="cm-dot{" filled" if i <= idx else ""}"></span>'
        for i in range(len(_LEVEL_ORDER))
    )
    return f'<div class="cm-level-meter">{dots}<span class="cm-level-label">{level}</span></div>'


def _bridge_html(source_lang: str, target_lang: str) -> str:
    return (
        f'<div class="cm-bridge">'
        f'<span class="cm-lang-pill">{source_lang}</span>'
        f'<span class="cm-arrow">&#8594;</span>'
        f'<span class="cm-lang-pill">{target_lang}</span>'
        f'</div>'
    )


def _target_lang_to_code_lang(target_lang: str):
    return gr.update(language=_LANG_TO_CODE_LANG.get(target_lang, "python"))


def _steps_html(steps: list[str]) -> str:
    parts = ['<div class="cm-steps">']
    for i, label in enumerate(steps, start=1):
        parts.append(f'<div class="cm-step"><span class="cm-step-num">{i:02d}</span>{label}</div>')
        if i < len(steps):
            parts.append('<div class="cm-step-divider"></div>')
    parts.append("</div>")
    return "".join(parts)


_STEPS_CODE_MENTOR = _steps_html(["Paste your code", "Pick a level", "Get a mentor-grade review"])
_STEPS_ROSETTA = _steps_html(["Paste your code", "Select a language", "Translate"])


def _steps_for_tab(evt: gr.SelectData):
    """Swaps the step strip to match whichever tab the user just switched to."""
    label = getattr(evt, "value", "") or ""
    if "Rosetta" in label or evt.index == 1:
        return _STEPS_ROSETTA
    return _STEPS_CODE_MENTOR


def generate_complexity_chart(detected_complexity):
    """Generates a Plotly graph comparing standard Big-O curves, highlighting the detected one.
    Backgrounds are left transparent (no fixed plotly_white/plotly_dark template) so the
    surrounding card's --cm-surface color shows through in both light and dark mode; text,
    axis, and gridline colors are re-themed live via CSS (see PLOTLY THEME SYNC in theme.py)."""
    fig = go.Figure()

    if not detected_complexity or detected_complexity == "N/A" or detected_complexity not in ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)']:
        # Return an empty, styled figure if no valid complexity is provided
        fig.update_layout(
            title="Time Complexity: Not applicable to this input",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        return fig

    # Generate X values (Input Size)
    x = list(range(1, 11))
    
    # Generate Y values (Operations) for standard curves
    curves = {
        'O(1)': [1 for _ in x],
        'O(log n)': [math.log2(n) if n > 1 else 0 for n in x],
        'O(n)': x,
        'O(n log n)': [n * math.log2(n) if n > 1 else 0 for n in x],
        'O(n^2)': [n**2 for n in x]
    }

    # Plot all curves
    for label, y_values in curves.items():
        if label == detected_complexity:
            # Highlight the user's actual complexity in bold indigo — a fixed accent that
            # reads clearly on both a light and a dark card background.
            fig.add_trace(go.Scatter(x=x, y=y_values, mode='lines+markers', name=f"Your Code: {label}", line=dict(color='#6366f1', width=5)))
        else:
            # Fade out the background comparisons — mid slate-gray keeps enough contrast in
            # both modes, unlike 'lightgray' which nearly disappears on a dark card.
            fig.add_trace(go.Scatter(x=x, y=y_values, mode='lines', name=label, line=dict(color='#94a3b8', width=2, dash='dot')))

    fig.update_layout(
        title="Algorithmic Time Complexity",
        xaxis_title="Input Elements (n)",
        yaxis_title="Operations Required",
        yaxis=dict(range=[0, 30]), # Cap Y-axis so O(n^2) doesn't squash the smaller curves
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


@safe_call
def handle_submit(code_input: str, level: str, traceback_input: str, session_id: str, progress=gr.Progress()):
    if not code_input or not code_input.strip():
        empty_result = {
            "breakdown": "Please paste a code snippet (or type a question) before submitting.",
            "analogy": "", "bugs": [], "doc_findings": None, "optimized_snippet": "", "time_complexity": "N/A"
        }
        return empty_result, "No request sent — input was empty."

    progress(0.1, desc="Preparing request…")
    user_message = code_input
    if traceback_input and traceback_input.strip():
        user_message += f"\n\n--- User-provided traceback/error log ---\n{traceback_input}"

    progress(0.4, desc="Agent is reasoning (may call tools)…")
    parsed, trace = analyze_code(user_message, level, session_id)
    progress(1.0, desc="Done.")
    return parsed, trace


@safe_call
def handle_translate(source_code: str, source_lang: str, target_lang: str, progress=gr.Progress()):
    if not source_code or not source_code.strip():
        return "", "Please paste some code first."

    from langchain_groq import ChatGroq
    progress(0.2, desc="Translating…")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

    prompt = f"""Translate the following {source_lang} code into idiomatic {target_lang}.
Respond with ONLY valid JSON, no markdown fences, matching exactly this schema:
{{
    "translated_code": "Raw string of the translated code. CRITICAL: format it exactly as a human developer would in a real file — every statement, brace, and block on its own line, using literal \\n newline characters between lines and consistent indentation. Do NOT collapse the code onto a single line.",
    "differences": "Markdown string explaining the key differences, formatted as a bulleted list: each bullet starts with '- ' on its own line (a literal \\n before every '- '), 1-2 sentences per bullet. Do NOT run bullets together in one paragraph.",
    "warnings": "String explaining any caveats or paradigm shifts."
}}

Source code ({source_lang}):
{source_code}"""

    progress(0.6, desc="Waiting for model…")
    response = llm.invoke(prompt)

    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    result = json.loads(text)
    progress(1.0, desc="Done.")
    return result.get("translated_code", ""), result.get("differences", "")


with gr.Blocks(theme=CODEMENTOR_THEME, css=CUSTOM_CSS, head=HEAD_HTML, title="Code Mentor") as demo:
    session_id = gr.State(value=lambda: str(uuid.uuid4()))

    with gr.Row():
        with gr.Column(scale=5):
            gr.HTML(
                '<div class="cm-header-wrap">'
                '<div class="cm-wordmark">Code Mentor<span class="dot">.</span></div>'
                '<div class="cm-tagline">Adaptive code explanations · real bug fixes · verified documentation</div>'
                '</div>'
            )
        with gr.Column(scale=1, min_width=110, elem_id="cm-theme-toggle-row"):
            theme_toggle_btn = gr.Button("🌙 Night mode", elem_id="cm-theme-toggle", size="sm")
            theme_toggle_btn.click(fn=None, inputs=None, outputs=None, js=THEME_TOGGLE_JS)

    steps_out = gr.HTML(value=_STEPS_CODE_MENTOR)

    with gr.Tabs() as tabs:
        with gr.Tab("💡 Code Mentor"):
            with gr.Row():
                # LEFT COLUMN (Inputs) — styled as "the desk": a workspace card
                with gr.Column(scale=1):
                    # FIX 1: Changed gr.Group to gr.Column to restore natural breathing room
                    with gr.Column(elem_classes=["cm-desk-card"]):
                        gr.Markdown("Analyze", elem_classes=["cm-section-title"])
                        code_input = gr.Textbox(
                            label="Source Code", lines=12,
                            placeholder="Paste Python, JS, Java, or C++ here…",
                        )
                        traceback_input = gr.Textbox(label="Error Traceback (Optional)", lines=2, placeholder="Paste a raw error log…")
                        level = gr.Dropdown(choices=_LEVEL_ORDER, value="Beginner", label="Explanation Depth", interactive=True, elem_id="cm-depth-selector")
                        level_meter = gr.HTML(value=_level_meter_html("Beginner"))
                        submit_btn = gr.Button("Analyze Code", variant="primary", size="lg", elem_classes=["cm-primary-btn"])

                    # FIX 2: Changed gr.Group to gr.Column here as well
                    with gr.Column(elem_classes=["cm-followup-card"]):
                        gr.Markdown("Ask a follow-up", elem_classes=["cm-section-title"])
                        gr.Markdown("_The agent remembers your session. Press Enter to send!_", elem_classes=["cm-tagline"])
                        followup_input = gr.Textbox(label="Your Question", lines=2, placeholder="e.g., What happens if I remove line 4?")
                        followup_btn = gr.Button("Ask Question", variant="secondary")

                # RIGHT COLUMN (Outputs)
                with gr.Column(scale=2, variant="panel"):
                    with gr.Accordion("📈 Performance Graph", open=True, elem_classes=["cm-acc"]):
                        # The Plotly Graphic Component
                        complexity_out = gr.Plot()

                    with gr.Accordion("◆ Analogy & Concept", open=True, elem_classes=["cm-acc"]):
                        analogy_out = gr.Markdown(value=_EMPTY_ANALOGY)
                    with gr.Accordion("◆ Line-by-Line Breakdown", open=True, elem_classes=["cm-acc"]):
                        breakdown_out = gr.Markdown(value=_EMPTY_BREAKDOWN)
                    with gr.Accordion("◆ Bugs & Fixes", open=True, elem_classes=["cm-acc"]):
                        bugs_out = gr.Dataframe(headers=["Issue", "Fix"], wrap=True, interactive=False, value=_EMPTY_BUGS)
                    with gr.Accordion("◆ Optimized Code", open=True, elem_classes=["cm-acc"]):
                        code_out = gr.Code(language="python", wrap_lines=True)
                    with gr.Accordion("◆ Documentation Findings", open=False, elem_classes=["cm-acc"]):
                        docs_out = gr.Markdown(value=_EMPTY_DOCS)
                    with gr.Accordion("🔍 Agent Reasoning Trace", open=False, elem_classes=["cm-trace-accordion"]):
                        trace_out = gr.Textbox(show_label=False, interactive=False, lines=4, elem_classes=["cm-trace"])

            level.change(fn=_level_meter_html, inputs=level, outputs=level_meter)

            # --- Event Handlers ---
            def _submit_and_unpack(code_text, lvl, trace_text, sess_id):
                parsed, trace = handle_submit(code_text, lvl, trace_text, sess_id)
                if "error" in parsed:
                    # Return empty/fallback values including an empty plot on error
                    return (generate_complexity_chart("N/A"), "⚠️ Analysis Failed", f"**System Error:** {parsed['error']}", [["Error", "Check breakdown panel"]], "", _EMPTY_DOCS, trace)
                
                chart = generate_complexity_chart(parsed.get("time_complexity", "N/A"))
                
                return (
                    chart,
                    parsed.get("analogy", ""),
                    parsed.get("breakdown", ""),
                    _bugs_to_rows(parsed.get("bugs", [])),
                    parsed.get("optimized_snippet", ""),
                    parsed.get("doc_findings") or "No documentation lookup was needed.",
                    trace,
                )

            # Bind the button
            submit_btn.click(
                _submit_and_unpack,
                inputs=[code_input, level, traceback_input, session_id],
                outputs=[complexity_out, analogy_out, breakdown_out, bugs_out, code_out, docs_out, trace_out],
            )

            def _followup_and_unpack(question_text, lvl, sess_id):
                parsed, trace = handle_submit(question_text, lvl, "", sess_id)
                if "error" in parsed:
                    return (generate_complexity_chart("N/A"), "⚠️ Follow-up Failed", f"**System Error:** {parsed['error']}", [["Error", "Check breakdown panel"]], "", _EMPTY_DOCS, trace)
                
                chart = generate_complexity_chart(parsed.get("time_complexity", "N/A"))

                return (
                    chart,
                    parsed.get("analogy", ""),
                    parsed.get("breakdown", ""),
                    _bugs_to_rows(parsed.get("bugs", [])),
                    parsed.get("optimized_snippet", ""),
                    parsed.get("doc_findings") or "No documentation lookup was needed.",
                    trace,
                )

            # Bind both button and Enter key for follow-up
            followup_btn.click(
                _followup_and_unpack,
                inputs=[followup_input, level, session_id],
                outputs=[complexity_out, analogy_out, breakdown_out, bugs_out, code_out, docs_out, trace_out],
            )
            followup_input.submit(
                _followup_and_unpack,
                inputs=[followup_input, level, session_id],
                outputs=[complexity_out, analogy_out, breakdown_out, bugs_out, code_out, docs_out, trace_out],
            )

        # ---------------- TAB 2: Rosetta Stone ----------------
        with gr.Tab("🌐 Rosetta Stone"):
            gr.HTML(
                '<div class="cm-section-intro">'
                '<div class="cm-section-title-lg">Translate Core Logic</div>'
                '<div class="cm-tagline">See how different languages handle the same algorithms.</div>'
                '</div>'
            )
            with gr.Row():
                source_lang = gr.Dropdown(choices=["Python", "JavaScript", "Java", "C++"], value="Python", label="From", elem_id="cm-depth-selector")
                target_lang = gr.Dropdown(choices=["Python", "JavaScript", "Java", "C++"], value="JavaScript", label="To", elem_id="cm-depth-selector")
            bridge_out = gr.HTML(value=_bridge_html("Python", "JavaScript"))

            with gr.Row():
                with gr.Column(variant="panel"):
                    source_code = gr.Textbox(label="Source Code", lines=10)
                    translate_btn = gr.Button("Translate", variant="primary", elem_classes=["cm-primary-btn"])
                
                with gr.Column(variant="panel"):
                    translated_code = gr.Code(label="Translated Code", language="javascript", wrap_lines=True)
                    differences_out = gr.Markdown(label="Architectural Differences")

            source_lang.change(fn=_bridge_html, inputs=[source_lang, target_lang], outputs=bridge_out)
            target_lang.change(fn=_bridge_html, inputs=[source_lang, target_lang], outputs=bridge_out)
            target_lang.change(fn=_target_lang_to_code_lang, inputs=target_lang, outputs=translated_code)

            translate_btn.click(
                handle_translate,
                inputs=[source_code, source_lang, target_lang],
                outputs=[translated_code, differences_out],
            )

    tabs.select(fn=_steps_for_tab, outputs=steps_out)

if __name__ == "__main__":
    demo.launch()