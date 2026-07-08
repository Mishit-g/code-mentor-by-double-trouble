"""
agent.py — The Orchestrator

This is the only file that touches LangGraph directly. It wires:
  - the LLM (Groq, low temperature so JSON doesn't break)
  - the tools (from tools.py)
  - memory (MemorySaver, keyed by session_id/thread_id — this is what makes
    follow-up questions like "what if I removed line 4?" work without the
    user re-pasting the snippet)
  - a recursion_limit (so a confused agent can't loop forever)
  - trace capture (so the UI can show which tool fired, for which reason)
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphRecursionError

from tools import ALL_TOOLS
from prompts import PERSONAS

load_dotenv()

# temperature=0.2, not 0 — a little room for natural language in the "breakdown"
# and "analogy" fields, but low enough that the JSON structure stays reliable.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

memory = MemorySaver()

# One agent instance, reused across all requests. We do NOT bake a persona into
# it at creation time (via state_modifier) because the persona changes per
# request (user picks Beginner/Intermediate/Expert each submit) while thread_id
# memory needs to persist across that. So the persona is injected as a system
# message inside analyze_code() below, per call, instead.
agent = create_react_agent(
    model=llm,
    tools=ALL_TOOLS,
    checkpointer=memory,
)


def _extract_json(raw_text: str) -> dict:
    """The model is instructed to return pure JSON, but LLMs sometimes wrap it
    in ```json fences anyway. Strip those defensively before parsing."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)


def analyze_code(user_input: str, level_dropdown: str, session_id: str) -> tuple[dict, str]:
    """
    Main entry point called by app.py.

    Args:
        user_input: the code snippet (plus optional traceback context) the user submitted.
        level_dropdown: "Beginner" | "Intermediate" | "Expert"
        session_id: a per-browser-tab UUID (see app.py) — this becomes the
            LangGraph thread_id, which is what gives each user their own
            independent conversation memory.

    Returns:
        (parsed_dict, trace_string) — parsed_dict matches the schema in
        prompts.SYSTEM_BASE; trace_string is a human-readable log of which
        tools were called, for the "Agent Reasoning Trace" accordion.
    """
    system_prompt = PERSONAS[level_dropdown]

    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 10,
    }

    trace_log = []
    final_text = ""

    for event in agent.stream(
        {
            "messages": [
                SystemMessage(content=system_prompt, id="main_system_prompt"),
                HumanMessage(content=user_input),
            ]
        },
        config=config,
        stream_mode="values",
    ):
        last_msg = event["messages"][-1]

        # If the model asked to call a tool, log exactly what it called and why.
        if getattr(last_msg, "tool_calls", None):
            for tc in last_msg.tool_calls:
                trace_log.append(f"→ Tool: {tc['name']}  |  Input: {tc['args']}")
        # A final AI message with no further tool calls is the answer.
        elif getattr(last_msg, "type", None) == "ai" and not last_msg.tool_calls:
            final_text = last_msg.content

    trace_string = "\n".join(trace_log) if trace_log else "No tools were called for this request."

    parsed = _extract_json(final_text)
    return parsed, trace_string