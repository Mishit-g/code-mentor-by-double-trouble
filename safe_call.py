"""
safe_call.py — The Shield

One decorator, applied to every Gradio-facing handler in app.py. Its whole job
is: never let a raw Python traceback reach a judge's screen. Every failure mode
becomes a short, human-readable string instead.
"""

import functools
import json
from langgraph.errors import GraphRecursionError

try:
    import groq
except ImportError:
    groq = None


def safe_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GraphRecursionError:
            return (
                {"error": "Agent exceeded its step limit. The code may be too complex, "
                           "or the model got stuck reasoning. Try a shorter snippet."},
                "Trace unavailable — recursion limit hit.",
            )
        except json.JSONDecodeError:
            return (
                {"error": "The AI did not return valid JSON this time. Please try again."},
                "Trace unavailable — JSON parsing failed.",
            )
        except Exception as e:
            # groq.RateLimitError, groq.APIConnectionError, and anything unexpected
            # all fall through here so the app never crashes visibly.
            if groq and isinstance(e, getattr(groq, "RateLimitError", ())):
                return (
                    {"error": "Groq API rate limit hit. Wait about 10 seconds and try again."},
                    "Trace unavailable — rate limited.",
                )
            return ({"error": f"System fault: {str(e)}"}, "Trace unavailable — unexpected error.")
    return wrapper
