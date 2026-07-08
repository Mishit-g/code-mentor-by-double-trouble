"""
theme.py — Code Mentor's Visual Identity

CONCEPT: "The Margin Note"
A mentor doesn't rewrite your code — they annotate it. They circle the bug,
underline the clever bit, scribble a fix in the margin. That's the visual
metaphor here: an amber highlighter/chalk stroke is the one recurring accent,
appearing identically in both modes so the brand doesn't reset when the mode
flips.

Day mode  = "Notebook"   — cool paper-white, graphite ink, a marker-amber accent.
Night mode = "Chalkboard" — near-black slate, chalk-white ink, the *same* amber
             accent (now reading as chalk instead of highlighter).

TYPE SYSTEM
- Display  : Fraunces (italic) — a warm, high-contrast serif used only for
             the app title and section headers, set in italic to read like
             a mentor's handwritten margin note rather than a SaaS logotype.
- Body/UI  : Inter               — neutral, highly legible workhorse for
             every label, paragraph, and control.
- Mono     : JetBrains Mono      — real developer typeface, used for every
             code surface (inputs, outputs, the reasoning trace).

SIGNATURE ELEMENT
A hand-drawn "highlighter underline" (inline SVG, wobble-path) sits beneath
the app title and beneath the active tab. It's the one place the design
takes a visible risk; everything else stays quiet and disciplined.

--------------------------------------------------------------------------
HOW TO WIRE THIS IN (app.py is untouched — do this yourself when ready):

    from theme import CODEMENTOR_THEME, CUSTOM_CSS, HEAD_HTML, THEME_TOGGLE_JS

    with gr.Blocks(theme=CODEMENTOR_THEME, css=CUSTOM_CSS, head=HEAD_HTML,
                   title="Code Mentor") as demo:
        ...
        toggle_btn = gr.Button("🌙 Night mode", elem_id="cm-theme-toggle", size="sm")
        toggle_btn.click(fn=None, inputs=None, outputs=None, js=THEME_TOGGLE_JS)

That's a 3-line addition (import, one button, one .click) — nothing else in
your layout, handlers, or component order needs to change.
--------------------------------------------------------------------------
"""

import gradio as gr

# ---------------------------------------------------------------------------
# 1. HEAD INJECTION — fonts + an inline pre-paint script so the saved theme
#    (light/dark) applies before Gradio renders a single pixel (no flash).
# ---------------------------------------------------------------------------

HEAD_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500;1,9..144,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script>
  (function () {
    try {
      var saved = localStorage.getItem('cm-theme') || 'light';
      document.documentElement.setAttribute('data-theme', saved);
      if (saved === 'dark') { document.documentElement.classList.add('dark'); }
    } catch (e) {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  })();
</script>
"""

# ---------------------------------------------------------------------------
# 2. GRADIO THEME OBJECT — base layout/spacing/font tokens. Color surfaces
#    are intentionally left neutral here; CUSTOM_CSS below owns the actual
#    palette via CSS variables so both modes can share one theme object.
# ---------------------------------------------------------------------------

CODEMENTOR_THEME = gr.themes.Base(
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "SFMono-Regular", "monospace"],
    radius_size=gr.themes.sizes.radius_lg,
    spacing_size=gr.themes.sizes.spacing_md,
).set(
    body_background_fill="var(--cm-bg)",
    body_text_color="var(--cm-text)",
    body_text_color_subdued="var(--cm-text-muted)",
    background_fill_primary="var(--cm-surface)",
    background_fill_secondary="var(--cm-surface-alt)",
    border_color_primary="var(--cm-border)",
    border_color_accent="var(--cm-accent)",
    color_accent="var(--cm-accent)",
    color_accent_soft="var(--cm-accent-soft)",
    block_background_fill="var(--cm-surface)",
    block_border_color="var(--cm-border)",
    block_label_background_fill="var(--cm-surface-alt)",
    block_label_border_color="var(--cm-border)",
    block_label_text_color="var(--cm-text-muted)",
    block_title_text_color="var(--cm-text)",
    input_background_fill="var(--cm-surface)",
    input_border_color="var(--cm-border)",
    input_placeholder_color="var(--cm-text-muted)",
    button_primary_background_fill="var(--cm-accent)",
    button_primary_background_fill_hover="var(--cm-accent-hover)",
    button_primary_text_color="#1B1204",
    button_secondary_background_fill="var(--cm-surface-alt)",
    button_secondary_text_color="var(--cm-text)",
    button_secondary_border_color="var(--cm-border)",
    table_even_background_fill="var(--cm-surface)",
    table_odd_background_fill="var(--cm-surface-alt)",
    table_border_color="var(--cm-border)",
    table_row_focus="var(--cm-accent-soft)",
)

# ---------------------------------------------------------------------------
# 3. CUSTOM CSS — the palette, type scale, and the signature underline.
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
/* ============================================================
   DESIGN TOKENS
   ============================================================ */
:root, html[data-theme="light"] {
  --cm-bg:            #EEF0F4;
  --cm-surface:       #FFFFFF;
  --cm-surface-alt:   #E4E7EE;
  --cm-border:        #D7DBE3;
  --cm-text:          #1B2030;
  --cm-text-muted:    #5B6272;
  --cm-accent:        #E8A33D;
  --cm-accent-hover:  #D6912E;
  --cm-accent-soft:   rgba(232, 163, 61, 0.16);
  --cm-good:          #2F9E6E;
  --cm-good-soft:     rgba(47, 158, 110, 0.12);
  --cm-bad:           #C7594A;
  --cm-bad-soft:      rgba(199, 89, 74, 0.10);
  --cm-shadow:        0 1px 2px rgba(27, 32, 48, 0.04), 0 8px 24px rgba(27, 32, 48, 0.06);
  color-scheme: light;
}

html[data-theme="dark"] {
  --cm-bg:            #14171F;
  --cm-surface:       #1C2029;
  --cm-surface-alt:   #242A36;
  --cm-border:        #303646;
  --cm-text:          #EDEFF4;
  --cm-text-muted:    #9BA2B4;
  --cm-accent:        #F2B559;
  --cm-accent-hover:  #F7C578;
  --cm-accent-soft:   rgba(242, 181, 89, 0.14);
  --cm-good:          #63D6AE;
  --cm-good-soft:     rgba(99, 214, 174, 0.10);
  --cm-bad:           #E28B7D;
  --cm-bad-soft:      rgba(226, 139, 125, 0.10);
  --cm-shadow:        0 1px 2px rgba(0, 0, 0, 0.25), 0 12px 32px rgba(0, 0, 0, 0.35);
  color-scheme: dark;
}

/* ============================================================
   GRADIO INTERNAL VARIABLE OVERRIDE
   Every built-in Gradio component (dropdown chrome, the small corner
   "label" chip on Plot/Code/Dataframe, table headers, etc.) reads its
   colors from Gradio's own CSS custom properties — not from our tokens
   directly. theme.set() forwards most of these, but a few (block-label
   background, table stripe colors) fall back to Gradio's hardcoded
   defaults if left unset, which is why dropdowns/corner-chips/tables
   stayed dark in both modes. Re-declaring them here, with !important,
   guarantees they track our light/dark tokens instead.
   ============================================================ */
.gradio-container {
  --body-background-fill: var(--cm-bg) !important;
  --body-text-color: var(--cm-text) !important;
  --body-text-color-subdued: var(--cm-text-muted) !important;
  --background-fill-primary: var(--cm-surface) !important;
  --background-fill-secondary: var(--cm-surface-alt) !important;
  --border-color-primary: var(--cm-border) !important;
  --border-color-accent: var(--cm-accent) !important;
  --color-accent: var(--cm-accent) !important;
  --color-accent-soft: var(--cm-accent-soft) !important;
  --block-background-fill: var(--cm-surface) !important;
  --block-border-color: var(--cm-border) !important;
  --block-label-background-fill: var(--cm-surface-alt) !important;
  --block-label-border-color: var(--cm-border) !important;
  --block-label-text-color: var(--cm-text-muted) !important;
  --block-title-text-color: var(--cm-text) !important;
  --input-background-fill: var(--cm-surface) !important;
  --input-border-color: var(--cm-border) !important;
  --input-placeholder-color: var(--cm-text-muted) !important;
  --table-even-background-fill: var(--cm-surface) !important;
  --table-odd-background-fill: var(--cm-surface-alt) !important;
  --table-border-color: var(--cm-border) !important;
  --neutral-50: var(--cm-surface) !important;
  --neutral-100: var(--cm-surface-alt) !important;
  --neutral-900: var(--cm-text) !important;
  --neutral-950: var(--cm-text) !important;
}

/* Corner chips ("Plot", "Code", filename tags) and any listbox/combobox
   chrome — targeted via stable ARIA/testid hooks rather than Svelte's
   auto-generated class names, which change between Gradio versions. */
.block-label,
[data-testid="block-label"],
[role="listbox"],
[role="combobox"],
[data-testid="dropdown"] {
  background: var(--cm-surface-alt) !important;
  color: var(--cm-text-muted) !important;
  border-color: var(--cm-border) !important;
  border-radius: 12px !important;
}

/* ============================================================
   GLOBAL ROUNDING PASS — every input-like surface (textboxes, the
   Beginner/Intermediate/Expert and language dropdowns, their outer
   "block" wrapper) shares one consistent, generously rounded corner
   radius so nothing reads as a sharp-edged default control.
   ============================================================ */
.gradio-container .block,
.gradio-container .form,
.gr-box,
.wrap,
.wrap-inner,
select,
ul[role="listbox"],
li[role="option"] {
  border-radius: 14px !important;
}

/* CodeMirror (powers gr.Code) ships its own theme classes with high
   specificity, independent of the Gradio theme above — re-themed
   explicitly so the snippet/translated-code panes track light/dark too. */
.cm-editor, .cm-editor.cm-focused,
.cm-scroller, .cm-gutters, .cm-content {
  background: var(--cm-surface) !important;
  color: var(--cm-text) !important;
  border-color: var(--cm-border) !important;
}
.cm-gutters { color: var(--cm-text-muted) !important; }
.cm-activeLine, .cm-activeLineGutter { background: var(--cm-accent-soft) !important; }

/* ============================================================
   TOP ACCENT BAR — a quiet nod to a diff gutter: three narrow stripes
   in the same three semantic colors used throughout (issue / accent / fix)
   ============================================================ */
.gradio-container::before {
  content: "";
  display: block;
  height: 4px;
  width: 100%;
  background: linear-gradient(90deg, var(--cm-bad) 0 33%, var(--cm-accent) 33% 66%, var(--cm-good) 66% 100%);
  opacity: 0.85;
  margin-bottom: 4px;
  border-radius: 0 0 4px 4px;
}
.gradio-container, .gradio-container * {
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.gradio-container {
  background: var(--cm-bg) !important;
  color: var(--cm-text) !important;
  font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
  /* Full-bleed layout: use the whole viewport width instead of pinning to a
     fixed max-width, with responsive side padding so content never touches
     the edge on very wide monitors. */
  width: 100% !important;
  max-width: 100% !important;
  padding-left: clamp(16px, 3.5vw, 56px) !important;
  padding-right: clamp(16px, 3.5vw, 56px) !important;
  box-sizing: border-box !important;
}

/* Text color does not cascade cleanly through Gradio's own Tailwind "prose"
   utility classes and per-component text tokens, so it's forced explicitly
   on every text-bearing element rather than relying on inheritance. */
.gradio-container p,
.gradio-container span,
.gradio-container li,
.gradio-container h1, .gradio-container h2, .gradio-container h3,
.gradio-container h4, .gradio-container h5, .gradio-container h6,
.gradio-container label,
.gradio-container .prose,
.gradio-container .prose *,
.gradio-container .md,
.gradio-container .markdown,
.gradio-container .gr-markdown,
.gradio-container .gr-text-input,
.gradio-container .wrap,
.gradio-container .cell,
.gradio-container td, .gradio-container th {
  color: var(--cm-text) !important;
}

footer { display: none !important; }

/* Panels, accordions, rows rendered as "gr-block" cards */
.gr-block.gr-box, .block, .form, .panel, .gr-panel {
  background: var(--cm-surface) !important;
  border-color: var(--cm-border) !important;
}

.gr-panel, .panel {
  border-radius: 14px !important;
  box-shadow: var(--cm-shadow);
}

label span, .gr-block label span, .block > label > span,
.gradio-container label > span:first-child {
  color: var(--cm-text-muted) !important;
  font-weight: 600 !important;
  font-size: 0.76rem !important;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* Placeholder text should read as muted, not full ink */
.gradio-container textarea::placeholder,
.gradio-container input::placeholder {
  color: var(--cm-text-muted) !important;
  opacity: 0.75;
  font-style: italic;
}

/* ============================================================
   HERO / HEADER — display type + the signature highlighter stroke
   ============================================================ */
.prose:has(h1) {
  padding-bottom: 6px;
}

.prose h1 {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-style: italic;
  font-weight: 600 !important;
  font-size: 2.4rem !important;
  letter-spacing: -0.01em;
  color: var(--cm-text) !important;
  display: inline-block;
  position: relative;
  margin-bottom: 0.4rem !important;
}

/* hand-drawn highlighter underline beneath the title */
.prose h1::after {
  content: "";
  display: block;
  width: 108%;
  height: 10px;
  margin-top: -4px;
  margin-left: -2%;
  background: var(--cm-accent);
  opacity: 0.55;
  border-radius: 3px;
  clip-path: polygon(
    0% 45%, 6% 20%, 14% 55%, 22% 15%, 30% 50%, 38% 25%, 46% 60%,
    54% 20%, 62% 50%, 70% 15%, 78% 55%, 86% 20%, 94% 50%, 100% 30%,
    100% 100%, 0% 100%
  );
}

.prose h1 + p, .prose p strong {
  font-family: 'Inter', sans-serif !important;
  color: var(--cm-text-muted) !important;
  font-weight: 400 !important;
}

/* Section headers inside panels ("### 1. Initial Analysis", etc.) — smaller
   display type, so hierarchy reads: title (h1) > section (h3) > body (p) */
.prose h3 {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-weight: 600 !important;
  font-size: 1rem !important;
  letter-spacing: 0.01em;
  color: var(--cm-text) !important;
  margin-top: 4px !important;
  margin-bottom: 10px !important;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--cm-border);
}

.prose p {
  font-size: 0.92rem !important;
  line-height: 1.55 !important;
  color: var(--cm-text-muted) !important;
  margin: 0 0 12px 0 !important;
}

.prose p:last-child { margin-bottom: 0 !important; }

/* Lists (bullet explanations, action-item style breakdowns) get real
   indentation and per-item spacing instead of collapsing into one run-on
   line — this is what actually gives model output "breathing room". */
.prose ul, .prose ol {
  margin: 4px 0 14px 0 !important;
  padding-left: 22px !important;
}

.prose li {
  font-size: 0.92rem !important;
  line-height: 1.6 !important;
  color: var(--cm-text-muted) !important;
  margin-bottom: 8px !important;
}

.prose li:last-child { margin-bottom: 0 !important; }

.prose li::marker { color: var(--cm-accent-hover); }

/* Inline `code` spans (e.g. naming a variable or function mid-sentence) */
.prose code {
  background: var(--cm-surface-alt) !important;
  color: var(--cm-text) !important;
  border: 1px solid var(--cm-border) !important;
  border-radius: 6px !important;
  padding: 1px 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.85em !important;
}

.prose em, .prose i {
  color: var(--cm-text-muted) !important;
  font-size: 0.85rem !important;
}

/* ============================================================
   TABS — styled like editor tabs, active tab gets the same underline motif
   ============================================================ */
.tab-nav {
  border-bottom: none !important;
  background: var(--cm-surface-alt) !important;
  border: 1px solid var(--cm-border) !important;
  border-radius: 999px !important;
  padding: 4px !important;
  gap: 2px;
  display: inline-flex !important;
  width: fit-content;
  margin-bottom: 18px;
}

.tab-nav button {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-style: italic;
  font-weight: 600 !important;
  color: var(--cm-text-muted) !important;
  border: none !important;
  background: transparent !important;
  padding: 8px 20px !important;
  border-radius: 999px !important;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.tab-nav button:hover {
  color: var(--cm-text) !important;
  background: var(--cm-border) !important;
}

.tab-nav button.selected {
  color: #1B1204 !important;
  background: var(--cm-accent) !important;
  box-shadow: none;
}

/* ============================================================
   ACCORDIONS — quiet by default, accent on open state
   ============================================================ */
.gr-accordion, .accordion {
  border: 1px solid var(--cm-border) !important;
  border-radius: 12px !important;
  background: var(--cm-surface) !important;
  overflow: hidden;
  margin-bottom: 10px !important;
}

.gr-accordion .label-wrap, .accordion > .label-wrap {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-weight: 600 !important;
  color: var(--cm-text) !important;
  padding: 12px 14px !important;
}

.gr-accordion .label-wrap:hover { background: var(--cm-surface-alt) !important; }

.gr-accordion svg, .accordion svg { color: var(--cm-accent) !important; }

/* ============================================================
   BUTTONS
   ============================================================ */
button.primary, .gr-button-primary, .cm-primary-btn button {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px var(--cm-accent-soft);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

button.primary:hover, .gr-button-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px var(--cm-accent-soft);
}

button.secondary, .gr-button-secondary {
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
}

/* Dedicated look for the theme toggle button — compact pill, not a
   full-width Gradio button */
#cm-theme-toggle {
  display: inline-flex !important;
  width: auto !important;
  min-width: 0 !important;
  max-width: fit-content !important;
  flex: none !important;
  border-radius: 999px !important;
  padding: 4px 12px !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  line-height: 1.4 !important;
  background: var(--cm-surface-alt) !important;
  color: var(--cm-text) !important;
  border: 1px solid var(--cm-border) !important;
  box-shadow: none !important;
  min-height: 0 !important;
}

#cm-theme-toggle:hover {
  border-color: var(--cm-accent) !important;
  transform: none !important;
}

/* Its parent column/row shouldn't stretch to fill available width */
#cm-theme-toggle-row {
  display: flex !important;
  justify-content: flex-end !important;
  gap: 6px;
}

/* ============================================================
   INPUTS — textboxes, dropdowns, code panes
   ============================================================ */
textarea, input[type="text"], input[type="number"], select {
  background: var(--cm-surface) !important;
  color: var(--cm-text) !important;
  border: 1px solid var(--cm-border) !important;
  border-radius: 14px !important;
  font-family: 'Inter', sans-serif !important;

}

textarea:focus, input:focus, select:focus {
  border-color: var(--cm-accent) !important;
  box-shadow: 0 0 0 3px var(--cm-accent-soft) !important;
}

/* Anywhere code is shown or pasted (snippet box, optimized code, trace) */
.gr-code, code, pre, textarea[data-testid="textbox"] {
  font-family: 'JetBrains Mono', ui-monospace, monospace !important;
}

/* ============================================================
   DATAFRAME — the bugs/fixes table
   ============================================================ */
.dataframe, table {
  border-radius: 14px !important;
  overflow: hidden;
  border: 1px solid var(--cm-border) !important;
}

.dataframe thead th {
  background: var(--cm-surface-alt) !important;
  color: var(--cm-text-muted) !important;
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.dataframe tbody td {
  background: var(--cm-surface) !important;
  color: var(--cm-text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* first column of the bugs table reads as an "issue" callout */
.dataframe tbody td:first-child {
  border-left: 3px solid var(--cm-bad);
}

/* ============================================================
   LEVEL DROPDOWN — The Brute Force ID Fix
   ============================================================ */
/* 1. Breathing room below the label */
#cm-depth-selector {
  margin-top: 6px !important; 
  width: 100% !important;
}

/* 2. Carpet-bomb every internal wrapper Gradio uses to force height */
#cm-depth-selector .wrap,
#cm-depth-selector .wrap-inner,
#cm-depth-selector .secondary-wrap {
  min-height: 48px !important;
  border-radius: 14px !important;
  box-sizing: border-box !important;
}

/* 3. Force the padding directly onto the input and its immediate container */
#cm-depth-selector .wrap-inner,
#cm-depth-selector input {
  padding-top: 10px !important;
  padding-bottom: 10px !important;
  display: flex !important;
  align-items: center !important;
}



/* ============================================================
   PLOT CARD — Big-O chart gets the same card treatment as everything else
   ============================================================ */
.plot-container, .gr-plot {
  background: var(--cm-surface) !important;
  border-radius: 14px !important;
  border: 1px solid var(--cm-border) !important;
  padding: 6px !important;
}

/* ============================================================
   PLOTLY THEME SYNC — the chart is generated server-side with a
   transparent background (see generate_complexity_chart in app.py), so
   the card's own --cm-surface shows through in both modes. Plotly bakes
   most colors as inline SVG styles/attrs; a stylesheet rule marked
   !important still wins over those, so title/axis/legend text, gridlines,
   and axis lines can be re-themed here without regenerating the figure.
   ============================================================ */
.js-plotly-plot .main-svg {
  background: transparent !important;
}
.js-plotly-plot text {
  fill: var(--cm-text) !important;
}
.js-plotly-plot .xgrid, .js-plotly-plot .ygrid {
  stroke: var(--cm-border) !important;
}
.js-plotly-plot .xaxislayer-above path,
.js-plotly-plot .yaxislayer-above path,
.js-plotly-plot .xaxislayer-above line,
.js-plotly-plot .yaxislayer-above line,
.js-plotly-plot .zerolinelayer path {
  stroke: var(--cm-border) !important;
}
.js-plotly-plot .modebar-btn path {
  fill: var(--cm-text-muted) !important;
}
.js-plotly-plot .modebar {
  background: transparent !important;
}

/* ============================================================
   SCROLLBAR — quiet, on-brand
   ============================================================ */
* { scrollbar-width: thin; scrollbar-color: var(--cm-border) transparent; }
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb { background: var(--cm-border); border-radius: 8px; }
*::-webkit-scrollbar-thumb:hover { background: var(--cm-text-muted); }

/* ============================================================
   ACCESSIBILITY
   ============================================================ */
*:focus-visible {
  outline: 2px solid var(--cm-accent) !important;
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
  }
}

/* ============================================================
   HEADER WORDMARK — a dedicated banner block, distinct from the plain
   gr.Markdown title used before. Sits above the step strip.
   ============================================================ */
.cm-header-wrap {
  padding: 4px 2px 20px 2px;
  border-bottom: 1px solid var(--cm-border);
  margin-bottom: 22px;
}

.cm-wordmark {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-style: italic;
  font-weight: 600;
  font-size: 2.3rem;
  color: var(--cm-text);
  letter-spacing: -0.01em;
  line-height: 1.1;
}
.cm-wordmark .dot { color: var(--cm-accent); }

.cm-tagline {
  font-family: 'Inter', sans-serif;
  font-size: 0.86rem;
  color: var(--cm-text-muted);
  margin-top: 6px;
}

/* ---- Onboarding step strip: "01 Paste → 02 Pick a level → 03 Review" ---- */
.cm-steps {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 2px 2px 22px 2px;
  flex-wrap: wrap;
}
.cm-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 0.86rem;
  color: var(--cm-text-muted);
}
.cm-step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.76rem;
  color: var(--cm-accent-hover);
  font-weight: 600;
}
.cm-step-divider {
  width: 22px;
  height: 1px;
  background: var(--cm-border);
}

/* ============================================================
   DESK / FOLLOW-UP CARDS — the input side reads as a distinct "workspace"
   panel, separate from the plain form fields Gradio renders by default.
   ============================================================ */
.cm-desk-card, .cm-followup-card {
  background: var(--cm-surface) !important;
  border: 1px solid var(--cm-border) !important;
  border-radius: 14px !important;
  padding: 24px !important; /* Increased padding for breathing room */
  box-shadow: var(--cm-shadow);
}

.cm-followup-card {
  border-left: 3px solid var(--cm-accent) !important;
  margin-top: 18px !important;
}

/* THE "GREY CURVATURE" FIX: 
   Gradio wraps inputs inside .block, .form, and fieldset tags. We must 
   aggressively strip the background and borders from ALL of these layers 
   when they live inside our custom cards or Rosetta row, otherwise their 
   grey backgrounds leak through the corners. 
*/
.cm-desk-card .block,
.cm-desk-card .form,
.cm-desk-card fieldset,
.cm-followup-card .block,
.cm-followup-card .form,
.cm-followup-card fieldset,
.cm-rosetta-row .block,
.cm-rosetta-row .form,
.cm-rosetta-row fieldset {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

/* Ensure the elements inside don't collapse their margins */
.cm-desk-card > .block,
.cm-followup-card > .block {
  margin-bottom: 0 !important; /* Let the gr.Column handle the gap */
}

/* Hide Gradio's pointless drag-to-resize handles on static blocks */
.cm-desk-card [class*="resize-handle" i],
.cm-followup-card [class*="resize-handle" i],
.cm-header-wrap [class*="resize-handle" i],
.cm-section-intro [class*="resize-handle" i] {
  display: none !important;
}

/* Header spacing - Reduced margin to pull the inputs up */
.cm-section-title {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-style: italic;
  font-weight: 600 !important;
  font-size: 1.08rem !important;
  color: var(--cm-text) !important;
  margin: 0 0 2px 0 !important; /* Reduced from 16px to bring the box up */
  padding-bottom: 4px !important;
  border-bottom: 1px solid var(--cm-border) !important;
}

/* Force the first block (Source Code) to sit tighter against the title line */
.cm-desk-card > .block:first-of-type,
.cm-followup-card > .block:first-of-type {
  margin-top: 4px !important; 
}

/* ============================================================
   ROSETTA STONE INTRO — mirrors .cm-header-wrap's spacing rules so the
   tab's title + tagline read as one calm block, not two stacked cards.
   ============================================================ */
.cm-section-intro {
  padding: 4px 2px 18px 2px;
  border-bottom: 1px solid var(--cm-border);
  margin-bottom: 20px;
}
.cm-section-title-lg {
  font-family: 'Fraunces', ui-serif, Georgia, serif !important;
  font-style: italic;
  font-weight: 600;
  font-size: 1.5rem;
  color: var(--cm-text);
  margin-bottom: 6px;
}

/* ============================================================
   LEVEL METER — a 3-dot ordinal indicator (Beginner < Intermediate <
   Expert) that tracks the dropdown live.
   ============================================================ */
.cm-level-meter {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 2px 0 2px;
}
.cm-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--cm-border);
  display: inline-block;
  transition: background-color 0.15s ease;
}
.cm-dot.filled { background: var(--cm-accent); }
.cm-level-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.74rem;
  color: var(--cm-text-muted);
  margin-left: 4px;
}

/* ============================================================
   TERMINAL-STYLE REASONING TRACE — the "dev tool" half. Rendered as a
   dark console regardless of light/dark mode, amber text, monospace.
   ============================================================ */
.cm-trace-accordion { border-radius: 12px !important; overflow: hidden !important; }
.cm-trace textarea {
  background: #14171F !important;
  color: var(--cm-accent) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.85rem !important;
  border: none !important;
}

/* ============================================================
   ROSETTA STONE BRIDGE — "Python → JavaScript" pill readout above the
   translate panel, kept in sync with the two language dropdowns.
   ============================================================ */
.cm-bridge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin: 6px 0 16px 0;
}
.cm-bridge .cm-lang-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  background: var(--cm-surface);
  border: 1px solid var(--cm-border);
  border-radius: 999px;
  padding: 5px 16px;
  color: var(--cm-text);
  font-weight: 600;
}
.cm-bridge .cm-arrow {
  color: var(--cm-accent-hover);
  font-size: 1.15rem;
  font-family: 'JetBrains Mono', monospace;
}

/* ============================================================
   EMPTY-STATE COPY — italic, muted placeholder text shown in output
   panels before the first run, instead of a blank panel.
   ============================================================ */
.cm-empty-state {
  color: var(--cm-text-muted) !important;
  font-style: italic;
  font-size: 0.88rem !important;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 768px) {
  .prose h1 { font-size: 1.6rem !important; }
  .cm-wordmark { font-size: 1.7rem; }
  .cm-header-wrap { padding-left: 12px; padding-right: 12px; }
}
"""

# ---------------------------------------------------------------------------
# 4. THEME TOGGLE — bind to a gr.Button's .click(fn=None, js=THEME_TOGGLE_JS)
#    Flips data-theme on <html>, persists it, and updates the button's own
#    label so it always describes the mode you'd switch *to*.
# ---------------------------------------------------------------------------

THEME_TOGGLE_JS = """
() => {
  const root = document.documentElement;
  const current = root.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';

  root.setAttribute('data-theme', next);
  root.classList.toggle('dark', next === 'dark');
  document.body.classList.toggle('dark', next === 'dark');
  const container = document.querySelector('.gradio-container');
  if (container) container.classList.toggle('dark', next === 'dark');

  try { localStorage.setItem('cm-theme', next); } catch (e) {}

  const btn = document.getElementById('cm-theme-toggle');
  if (btn) {
    const label = next === 'light' ? '🌙 Night mode' : '☀️ Day mode';
    const span = btn.querySelector('span') || btn;
    span.textContent = label;
  }
}
"""