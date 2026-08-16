import os
import re
import time
import html
import json
import inspect
import importlib
import requests
import edge_tts

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from hooks_and_titling import (
    TITLE_FRAMES,
    FRAME_STACKING_NOTE,
    HOOK_FRAMEWORK,
    REHOOK_TECHNIQUES,
)
from humanizing import (
    BANNED_PHRASES,
    HUMANIZING_GUIDELINES,
    PACING_EXAMPLE,
)
from youtube_api import (
    extract_video_id,
    get_video_metadata,
    search_current_titles,
    QuotaExceededError,
)
from claim_pipeline import extract_claim_register

# =============================================================================
# V2 MODULES
# =============================================================================

strategies_module = importlib.import_module("strategies")
strategy_engine_module = importlib.import_module("strategy_engine")
governance_module = importlib.import_module("governance")
validator_module = importlib.import_module("validator")
control_plane_module = importlib.import_module("control_plane")


# =============================================================================
# APP
# =============================================================================

app = FastAPI()

AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.5-flash:generateContent"
)

WORDS_PER_MINUTE = 150

VOICES = [
    ("en-US-GuyNeural", "Guy (US male)"),
    ("en-US-JennyNeural", "Jenny (US female)"),
    ("en-GB-RyanNeural", "Ryan (UK male)"),
    ("en-GB-SoniaNeural", "Sonia (UK female)"),
    ("en-ZA-LukeNeural", "Luke (South African male)"),
    ("en-ZA-LeahNeural", "Leah (South African female)"),
]


# =============================================================================
# V2 COMPATIBILITY LAYER
# =============================================================================

def _module_callable(module, preferred_names):
    for name in preferred_names:
        fn = getattr(module, name, None)

        if callable(fn):
            return fn

    return None


def _call_flexible(fn, values):
    """
    Call a function using only arguments its signature accepts.

    This preserves compatibility with the existing V2 modules without
    requiring their function signatures to match main.py exactly.
    """

    if fn is None:
        return None

    try:
        sig = inspect.signature(fn)
    except Exception:
        return fn(**values)

    kwargs = {}

    for name, parameter in sig.parameters.items():

        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        if name in values:
            kwargs[name] = values[name]

    try:
        return fn(**kwargs)

    except TypeError:

        positional = []

        for name, parameter in sig.parameters.items():

            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            if name in values:
                positional.append(values[name])

        return fn(*positional)


def _json_safe(value):
    try:
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
    except Exception:
        return str(value)


# =============================================================================
# STRATEGY ENGINE ADAPTER
# =============================================================================

def select_strategy_map(
    topic,
    audience="",
    objective="",
    length_minutes=10,
    source_context="",
    creative_direction="",
):

    fn = _module_callable(
        strategy_engine_module,
        [
            "select_strategies",
            "build_strategy_map",
            "generate_strategy_map",
            "choose_strategies",
            "select_strategy_map",
        ],
    )

    if fn is None:
        raise RuntimeError(
            "strategy_engine.py does not expose a recognized "
            "strategy-selection function."
        )

    values = {
        "topic": topic,
        "audience": audience,
        "likely_audience": audience,
        "objective": objective,
        "video_objective": objective,
        "length_minutes": length_minutes,
        "duration_minutes": length_minutes,
        "video_length": length_minutes,

        "source_context": source_context,
        "source_material": source_context,
        "research": source_context,
        "creative_direction": creative_direction,
    }

    result = _call_flexible(
        fn,
        values,
    )

    if result is None:
        raise RuntimeError(
            "The strategy engine returned no strategy map."
        )

    return result


# =============================================================================
# GOVERNANCE ADAPTER
# =============================================================================

def get_governance_text(strategy_map=None):

    candidates = [
        "get_governance",
        "build_governance",
        "get_rules",
        "GOVERNANCE",
        "GOVERNANCE_RULES",
        "RULES",
    ]

    for name in candidates:

        obj = getattr(
            governance_module,
            name,
            None,
        )

        if callable(obj):

            try:

                result = _call_flexible(
                    obj,
                    {
                        "strategy_map": strategy_map,
                        "strategies": strategy_map,
                    },
                )

                if result is not None:
                    return _json_safe(result)

            except Exception:
                continue

        elif obj is not None:

            return _json_safe(obj)

    return (
        "Governance rules are defined in governance.py. "
        "Apply all applicable rules from that module."
    )


# =============================================================================
# VALIDATOR ADAPTER
# =============================================================================

def validate_generated_script(
    script_text,
    topic,
    outline,
    strategy_map,
    length_minutes,
    claim_register=None,
):

    fn = _module_callable(
        validator_module,
        [
            "validate_script",
            "validate",
            "run_validation",
            "run_validator",
            "check_script",
        ],
    )

    if fn is None:
        raise RuntimeError(
            "validator.py does not expose a recognized "
            "validation function."
        )

    governance_text = get_governance_text(
        strategy_map
    )

    values = {
        "script": script_text,
        "script_text": script_text,
        "topic": topic,
        "outline": outline,
        "approved_outline": outline,
        "strategy_map": strategy_map,
        "strategies": strategy_map,
        "governance": governance_text,
        "governance_rules": governance_text,
        "claim_register": claim_register,
        "claims": claim_register,
        "length_minutes": length_minutes,
        "target_minutes": length_minutes,
    }

    result = _call_flexible(
        fn,
        values,
    )

    if result is None:
        raise RuntimeError(
            "The validator returned no result."
        )

    return result


# =============================================================================
# GENERIC TEXT CONVERSION
# =============================================================================

def result_to_text(result):

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        return _json_safe(result)

    if isinstance(result, list):
        return _json_safe(result)

    return str(result)


def validation_status(validation):

    if isinstance(validation, dict):

        status = str(
            validation.get("status")
            or validation.get("overall_status")
            or validation.get("result")
            or ""
        ).upper()

        if status in {
            "CRITICAL",
            "FAIL",
            "FAILED",
            "BLOCK",
        }:
            return "CRITICAL"

        criticals = (
            validation.get("critical")
            or validation.get("criticals")
            or validation.get("critical_failures")
            or validation.get("errors")
        )

        if isinstance(criticals, list) and criticals:
            return "CRITICAL"

        if validation.get("passed") is False:
            return "CRITICAL"

        return "PASS"

    text = str(validation).upper()

    if "CRITICAL" in text and (
        "FAIL" in text
        or "BLOCK" in text
        or "FAILURE" in text
    ):
        return "CRITICAL"

    return "PASS"


# =============================================================================
# VIDEO STRUCTURE
# =============================================================================

STRUCTURE_TEMPLATE = """
1. Cold Open / Hook
   Establish the central curiosity immediately.
   Do not manufacture evidence or credentials.

2. Setup
   Establish the viewer's problem, situation or question.
   Make the viewer recognize themselves without unnecessary repetition.

3. Core Sections
   Use approximately four to six substantial sections depending on runtime.
   Each section must have a clear job.
   Develop the point before moving on.
   Use causal progression rather than a sequence of unrelated observations.

4. Rehooks
   Use only where they serve retention.
   Do not mechanically insert them every fixed number of minutes.

5. Climax / Central Resolution
   Resolve the main question or tension created by the opening.

6. Payoff
   Give the viewer the promised understanding or practical takeaway.

7. Outro / CTA
   Keep the CTA natural.
   Do not interrupt an unresolved high-tension moment.
"""


# =============================================================================
# V2 OUTLINE PROMPT
# =============================================================================

OUTLINE_PROMPT_TEMPLATE = """
You are the planning layer of a professional long-form YouTube writing system.

You are NOT writing the final script.

Create a precise, editable beat plan for:

TITLE / TOPIC:
{topic}

CREATOR DIRECTION:
{creative_direction}

SOURCE / RESEARCH MATERIAL:
{source_context}

TARGET LENGTH:
{length_minutes} minutes
Approximately {word_target} spoken words.

APPROVED STRATEGY MAP:
{strategy_map}

CLAIM REGISTER:
{claim_register}

Treat the claim register as the evidence boundary. Do not upgrade
source claims into independently verified facts.

GOVERNANCE:
{governance}

STRUCTURE:
{structure}

HOOK FRAMEWORK:
{hook_framework}

REHOOK OPTIONS:
{rehook_techniques}

The strategy map is authoritative.

Do NOT introduce unrelated psychological techniques simply because you know them.

Each strategy must have a specific job.

If source/research material was supplied:

- Use it as source material rather than inventing additional facts.
- Do not claim the source says something it does not say.
- Distinguish evidence from interpretation.
- Do not invent studies, statistics, researchers or quotations.
- Do not manufacture authority.

For every beat include:

[BEAT]
Purpose:
Viewer state:
Content:
Strategy:
Open loop action:
Payoff / closure:
Transition:

Rules:

- This is a plan, not narration.
- Do not fabricate studies, statistics, researchers, credentials or personal experiences.
- Do not treat psychological terminology as decoration.
- Do not force every strategy into the video.
- Do not create unnecessary open loops.
- Every open loop must have a planned payoff.
- Do not design a CTA that interrupts unresolved narrative tension.
- The final plan must be realistically executable within the target length.
"""


# =============================================================================
# V2 SCRIPT PROMPT
# =============================================================================

SCRIPT_PROMPT_TEMPLATE = """
You are the execution layer of a professional long-form YouTube writing system.

Write the complete spoken narration using ONLY the APPROVED OUTLINE below.

TOPIC:
{topic}

CREATOR DIRECTION:
{creative_direction}

SOURCE / RESEARCH MATERIAL:
{source_context}

TARGET:
{length_minutes} minutes
Approximately {word_target} words.

APPROVED STRATEGY MAP:
{strategy_map}

APPROVED OUTLINE:
{outline}

CLAIM REGISTER:
{claim_register}

Treat the claim register as the evidence boundary. Do not upgrade
source claims into independently verified facts.

GOVERNANCE:
{governance}

HUMANIZING GUIDELINES:
{humanizing_guidelines}

BANNED AI-LIKE PHRASES:
{banned_phrases}

PACING REFERENCE:
{pacing_example}

CORE RULE:

Execute the approved plan.

Do not redesign the video.

Do not add major sections that aren't in the outline.

Do not remove major beats unless necessary to stay within the target length.

SOURCE / RESEARCH:

If source material was supplied:

- Use it faithfully.
- Do not invent information and attribute it to the source.
- Do not invent studies, researchers, statistics or quotations.
- Do not turn an association into causation.
- Do not present interpretation as established fact.
- If the supplied material does not establish a claim, calibrate the language.

PERSONAL EXPERIENCE:

Never invent first-person memories, credentials, professional history,
client experiences or personal anecdotes for the creator.

Do not write things such as:

"I remember when..."
"I used to..."
"In my years of..."
"I learned this the hard way..."

unless that experience was explicitly supplied by the creator.

EVIDENCE:

Never invent studies, researchers, statistics or precise scientific findings.

If a claim cannot safely be supported from the supplied material,
calibrate the language rather than manufacturing certainty.

PSYCHOLOGY:

Use psychological concepts only when they improve viewer understanding.

Do not name a psychological effect simply to make the script sound
scientific.

STYLE:

Write naturally.

Use contractions.

Avoid robotic transitions.

Avoid repetitive rhetorical structures.

Do not repeatedly use the same sentence pattern.

Do not sound like an academic paper.

Do not announce the techniques being used.

Never say:

"open loop"
"rehook"
"climax"
"beat"
"pattern interrupt"
"foot-in-the-door"
"strategy map"

or other internal production terminology.

PACING:

Vary sentence length.

Use short sentences for emphasis.

Allow longer sentences when the thought genuinely requires them.

Do not mechanically force every sentence into a fixed length.

The narration should sound natural when spoken aloud.

OUTPUT:

Return ONLY the narration.

No title.
No headings.
No notes.
No analysis.
No production instructions.
"""


# =============================================================================
# TITLE / CONTENT ANALYSIS PROMPT
# =============================================================================

ANALYZE_PROMPT_TEMPLATE = """
You are the analysis layer of a professional YouTube content system.

The creator may have supplied a title/topic, research material,
or a source URL.

INPUT TYPE:
{input_type}

CREATOR'S TITLE / TOPIC:
{topic}

CREATOR'S RESEARCH / SOURCE MATERIAL:
{source_context}

CREATOR'S DIRECTION:
{creative_direction}

LIVE YOUTUBE CONTEXT:
{context_block}

TITLE TOOLKIT:
{title_frames}

{frame_stacking_note}

Your job is to determine what can legitimately be built from the
material supplied by the creator.

IMPORTANT:

The supplied research/source material is evidence/context.

Do not invent facts that are supposedly contained in the source.

Clearly distinguish:

- what the source actually supports
- reasonable interpretation
- creative framing
- claims that would require additional evidence

If the creator supplied only a topic, analyse the topic normally.

If the creator supplied research, use it as the foundation rather
than pretending the topic exists independently of the research.

If the creator supplied a URL but the contents have not been retrieved,
do not pretend that you have read the article.

Do NOT use fake numerical "viral scores".

Do NOT claim that a title is guaranteed to go viral.

Do NOT invent credentials, experience, clients or authority for the creator.

Return exactly:

ASSESSMENT:
What is already strong.

WEAKNESSES:
What is unclear, generic, weak or potentially misleading.

RECOMMENDATION:
KEEP, EDIT, or REPLACE.

OPTIMIZED TITLE:
One improved title if improvement is necessary.
If the original is already strong, return the original.

WHY:
A concise explanation.

AUDIENCE:
Likely audience.

CORE PROMISE:
What the viewer expects to receive.

CURIOSITY ANGLE:
What unanswered question makes the viewer want to continue.

SOURCE ROLE:
How the supplied material should influence the video.

EVIDENCE LIMITS:
What claims should not be made without additional evidence.
"""


# =============================================================================
# VIDEO INSPIRATION PROMPT
# =============================================================================

VIDEO_INSPIRATION_PROMPT_TEMPLATE = """
You are a YouTube content strategist.

A public YouTube video was supplied only as inspiration.

SOURCE TITLE:
{source_title}

SOURCE DESCRIPTION:
{source_description}

SOURCE TAGS:
{source_tags}

Create a genuinely different topic and title.

Do NOT copy the source's wording, structure, claims or distinctive phrasing.

TITLE FRAMES:
{title_frames}

{frame_stacking_note}

Never invent creator credentials.

Return:

TITLE:
<new title>

WHY:
<why this is a distinct angle>
"""


# =============================================================================
# GEMINI
# =============================================================================

def call_gemini(prompt: str) -> str:

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Missing GEMINI_API_KEY."
        )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(
        GEMINI_URL,
        headers=headers,
        json=body,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    try:

        return (
            data["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
            .strip()
        )

    except (
        KeyError,
        IndexError,
        TypeError,
    ):

        raise RuntimeError(
            "Gemini returned an unexpected response."
        )


# =============================================================================
# HTML
# =============================================================================

def esc(text: str) -> str:
    return html.escape(
        str(text or "")
    )


def page(body_html: str) -> str:

    return f"""
    <html>

    <head>

      <title>Ren Media V2</title>

      <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
      >

      <style>

        body {{
          font-family: sans-serif;
          max-width: 760px;
          margin: 20px auto;
          padding: 0 12px;
          line-height: 1.5;
        }}

        textarea,
        input,
        select {{
          box-sizing: border-box;
          width: 100%;
          padding: 10px;
          font-size: 16px;
        }}

        textarea {{
          min-height: 260px;
        }}

        button {{
          padding: 12px 20px;
          font-size: 16px;
          cursor: pointer;
        }}

        button:disabled {{
          cursor: wait;
          opacity: 0.6;
        }}

        .card {{
          border: 1px solid #ddd;
          border-radius: 10px;
          padding: 16px;
          margin: 14px 0;
        }}

        .critical {{
          border-left: 5px solid #c0392b;
          padding-left: 12px;
        }}

        .warning {{
          border-left: 5px solid #f39c12;
          padding-left: 12px;
        }}

        .pass {{
          border-left: 5px solid #27ae60;
          padding-left: 12px;
        }}

        .muted {{
          color: #666;
        }}

        #loading-overlay {{
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(255,255,255,0.96);
          z-index: 9999;
          text-align: center;
          padding-top: 35vh;
          font-size: 18px;
        }}

      </style>

    </head>

    <body>

      <div id="loading-overlay">

        Working&hellip;

        <br>

        <small>
          Please don't close this tab.
        </small>

      </div>

      <h2>Ren Media V2</h2>

      {body_html}

      <script>

        document.querySelectorAll("form")
          .forEach(function(form) {{

            form.addEventListener(
              "submit",
              function() {{

                const overlay =
                  document.getElementById(
                    "loading-overlay"
                  );

                if (overlay) {{
                  overlay.style.display = "block";
                }}

                form.querySelectorAll(
                  "button[type=submit]"
                ).forEach(
                  function(button) {{
                    button.disabled = true;
                  }}
                );

              }}
            );

          }});

      </script>

    </body>

    </html>
    """


# =============================================================================
# TITLE ANALYSIS PARSING
# =============================================================================

def parse_title_analysis(raw_text):

    fields = {
        "ASSESSMENT": "",
        "WEAKNESSES": "",
        "RECOMMENDATION": "",
        "OPTIMIZED TITLE": "",
        "WHY": "",
        "AUDIENCE": "",
        "CORE PROMISE": "",
        "CURIOSITY ANGLE": "",
        "SOURCE ROLE": "",
        "EVIDENCE LIMITS": "",
    }

    current = None

    for line in raw_text.splitlines():

        stripped = line.strip()

        matched = False

        for key in fields:

            prefix = key + ":"

            if stripped.upper().startswith(
                prefix
            ):

                current = key

                fields[key] = (
                    stripped[len(prefix):]
                    .strip()
                )

                matched = True

                break

        if not matched and current:

            fields[current] += (
                ("\n" if fields[current] else "")
                + stripped
            )

    if not fields["OPTIMIZED TITLE"]:

        fields["OPTIMIZED TITLE"] = (
            raw_text.strip()
        )

    return fields


def clean_title_text(title):

    title = str(title or "").strip()

    title = title.strip('"')
    title = title.strip("*")

    if title.count(")") > title.count("("):
        title = title.rstrip(")").rstrip()

    if title.count("]") > title.count("["):
        title = title.rstrip("]").rstrip()

    return title


# =============================================================================
# INPUT NORMALIZATION
# =============================================================================

def build_source_context(
    input_type,
    source_text="",
    source_url="",
):

    if input_type == "passage":

        return (
            "CREATOR-SUPPLIED RESEARCH / PASSAGE:\n\n"
            + source_text.strip()
        )

    if input_type == "url":

        return (
            "CREATOR-SUPPLIED SOURCE URL:\n\n"
            + source_url.strip()
            + "\n\n"
            "IMPORTANT: The URL contents have not been retrieved "
            "by this version of the system. Do not claim to have "
            "read or analysed the article itself."
        )

    return ""


# =============================================================================
# TITLE CONTEXT
# =============================================================================

def get_youtube_context(topic):

    if not YOUTUBE_API_KEY:

        return (
            "No live YouTube search data is configured. "
            "Use the title toolkit and general title principles.",
            "",
        )

    try:

        results = search_current_titles(
            topic,
            YOUTUBE_API_KEY,
            max_results=5,
        )

        if not results:

            return (
                "No current YouTube search data was found.",
                "",
            )

        lines = "\n".join(
            f"- {r['title']} "
            f"({r['view_count']} views, "
            f"published {r['published_at'][:10]})"
            for r in results
        )

        return (
            "Current YouTube search examples:\n"
            + lines,
            "",
        )

    except QuotaExceededError:

        return (
            "Live YouTube search quota is unavailable. "
            "Use the internal title toolkit instead.",
            "<p class='muted'>"
            "Live YouTube search quota unavailable."
            "</p>",
        )

    except Exception as exc:

        return (
            "Live YouTube search could not be completed. "
            "Use the internal title toolkit instead.",
            "<p class='muted'>"
            "Live title search unavailable: "
            f"{esc(exc)}"
            "</p>",
        )


# =============================================================================
# HOME
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    body_html = """
      <div class="card">

        <h3>Start a new video</h3>

        <p class="muted">
          Start with a title, topic, research passage,
          article URL, or YouTube video.
        </p>

        <form
          method="post"
          action="/analyze"
        >

          <label>
            <strong>How do you want to start?</strong>
          </label>

          <select
            name="input_type"
            id="input_type"
            required
          >

            <option value="topic">
              Title / Topic
            </option>

            <option value="passage">
              Research / Passage
            </option>

            <option value="url">
              Article / Research URL
            </option>

          </select>

          <br><br>

          <div id="topic_input">

            <label>
              <strong>Title or topic</strong>
            </label>

            <input
              name="topic"
              placeholder="e.g. why women lose interest fast"
            >

          </div>

          <div
            id="passage_input"
            style="display:none;"
          >

            <label>
              <strong>Research / passage</strong>
            </label>

            <textarea
              name="source_text"
              rows="14"
              placeholder="Paste research, a passage, notes, study material, or article text here..."
            ></textarea>

          </div>

          <div
            id="url_input"
            style="display:none;"
          >

            <label>
              <strong>Article / research URL</strong>
            </label>

            <input
              name="source_url"
              type="url"
              placeholder="https://..."
            >

          </div>

          <br>

          <label>
            <strong>What do you want to make from it?</strong>
          </label>

          <textarea
            name="creative_direction"
            rows="4"
            placeholder="Optional. Example: Explain this research in simple language for men 25–45."
          ></textarea>

          <br>

          <label>
            <strong>Target length in minutes</strong>
          </label>

          <input
            name="length_minutes"
            value="10"
            type="number"
            min="1"
            max="60"
            step="1"
            required
          >

          <br><br>

          <button type="submit">
            Analyze
          </button>

        </form>

      </div>

      <div class="card">

        <h3>Video inspiration</h3>

        <p class="muted">
          Use a public YouTube video only as inspiration for a genuinely different angle.
        </p>

        <form
          method="post"
          action="/video-inspiration"
        >

          <input
            name="video_url"
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            required
          >

          <br><br>

          <button type="submit">
            Find a Different Angle
          </button>

        </form>

      </div>

      <script>

        const inputType =
          document.getElementById("input_type");

        const topicInput =
          document.getElementById("topic_input");

        const passageInput =
          document.getElementById("passage_input");

        const urlInput =
          document.getElementById("url_input");

        function updateInputMode() {{

          topicInput.style.display = "none";
          passageInput.style.display = "none";
          urlInput.style.display = "none";

          if (inputType.value === "topic") {{
            topicInput.style.display = "block";
          }}

          if (inputType.value === "passage") {{
            passageInput.style.display = "block";
          }}

          if (inputType.value === "url") {{
            urlInput.style.display = "block";
          }}

        }}

        inputType.addEventListener(
          "change",
          updateInputMode
        );

        updateInputMode();

      </script>
    """

    return page(body_html)


# =============================================================================
# ANALYZE
# =============================================================================

@app.post(
    "/analyze",
    response_class=HTMLResponse,
)
async def analyze(
    input_type: str = Form("topic"),
    topic: str = Form(""),
    source_text: str = Form(""),
    source_url: str = Form(""),
    creative_direction: str = Form(""),
    length_minutes: str = Form("10"),
):

    if not GEMINI_API_KEY:

        return page(
            "<p class='critical'>"
            "Missing GEMINI_API_KEY."
            "</p>"
        )

    try:

        length = int(
            float(length_minutes)
        )

    except (ValueError, TypeError):

        length = 10

    if length < 1:
        length = 1

    if length > 60:
        length = 60

    input_type = (
        input_type or "topic"
    ).strip().lower()

    topic = topic.strip()
    source_text = source_text.strip()
    source_url = source_url.strip()
    creative_direction = (
        creative_direction.strip()
    )

    if input_type == "topic":

        if not topic:

            return page(
                "<p class='critical'>"
                "Please provide a title or topic."
                "</p>"
            )

        source_context = ""

    elif input_type == "passage":

        if not source_text:

            return page(
                "<p class='critical'>"
                "Please provide the research or passage."
                "</p>"
            )

        source_context = build_source_context(
            input_type,
            source_text=source_text,
            source_url=source_url,
        )

    elif input_type == "url":

        if not source_url:

            return page(
                "<p class='critical'>"
                "Please provide a source URL."
                "</p>"
            )

        source_context = build_source_context(
            input_type,
            source_text=source_text,
            source_url=source_url,
        )

    else:

        return page(
            "<p class='critical'>"
            "Unknown input type."
            "</p>"
        )

    try:

        claim_register = extract_claim_register(
            source_context
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Claim Register extraction failed:
              {esc(exc)}
            </p>
            """
        )

    analysis_topic = (
        topic
        if topic
        else creative_direction
        if creative_direction
        else "Create a useful video from the supplied source material."
    )

    context_block, quota_note = get_youtube_context(
        analysis_topic
    )

    title_frames_text = "\n".join(
        f"- {desc}"
        for desc in TITLE_FRAMES.values()
    )

    prompt = ANALYZE_PROMPT_TEMPLATE.format(
        input_type=input_type,
        topic=topic,
        source_context=source_context,
        creative_direction=creative_direction,
        context_block=context_block,
        title_frames=title_frames_text,
        frame_stacking_note=FRAME_STACKING_NOTE,
    )

    try:

        raw = call_gemini(prompt)

        analysis = parse_title_analysis(
            raw
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Analysis failed:
              {esc(exc)}
            </p>
            """
        )

    optimized_title = clean_title_text(
        analysis["OPTIMIZED TITLE"]
    )

    if not optimized_title:

        optimized_title = (
            topic
            or creative_direction
            or "Untitled video"
        )

    strategy_topic = optimized_title

    try:

        strategy_map = select_strategy_map(
            topic=strategy_topic,
            audience=analysis["AUDIENCE"],
            objective=analysis["CORE PROMISE"],
            length_minutes=length,
            source_context=source_context,
            creative_direction=creative_direction,
        )

    except Exception as exc:

        return page(
            f"""
            <div class="critical">

              <strong>
                Strategy engine error
              </strong>

              <p>
                {esc(exc)}
              </p>

            </div>
            """
        )

    strategy_text = result_to_text(
        strategy_map
    )

    body_html = f"""
      <h3>1. Analyze</h3>

      {quota_note}

      <div class="card">

        <strong>Assessment</strong>

        <p>
          {esc(analysis["ASSESSMENT"])}
        </p>

      </div>

      <div class="card">

        <strong>Weaknesses</strong>

        <p>
          {esc(analysis["WEAKNESSES"])}
        </p>

      </div>

      <div class="card">

        <strong>Recommendation</strong>

        <p>
          {esc(analysis["RECOMMENDATION"])}
        </p>

      </div>

      <div class="card">

        <strong>Source role</strong>

        <p>
          {esc(analysis["SOURCE ROLE"])}
        </p>

      </div>

      <div class="card">

        <strong>Evidence limits</strong>

        <p>
          {esc(analysis["EVIDENCE LIMITS"])}
        </p>

      </div>

      <form
        method="post"
        action="/strategy-map"
      >

        <input
          type="hidden"
          name="input_type"
          value="{esc(input_type)}"
        >

        <input
          type="hidden"
          name="source_context"
          value="{esc(source_context)}"
        >

        <input
          type="hidden"
          name="claim_register"
          value="{esc(_json_safe(claim_register))}"
        >

        <input
          type="hidden"
          name="creative_direction"
          value="{esc(creative_direction)}"
        >

        <label>
          <strong>
            Optimized title
          </strong>
        </label>

        <input
          name="topic"
          value="{esc(optimized_title)}"
          required
        >

        <br><br>

        <label>
          <strong>
            Audience
          </strong>
        </label>

        <input
          name="audience"
          value="{esc(analysis["AUDIENCE"])}"
        >

        <br><br>

        <label>
          <strong>
            Core promise
          </strong>
        </label>

        <textarea
          name="objective"
          rows="4"
        >{esc(analysis["CORE PROMISE"])}</textarea>

        <br><br>

        <label>
          <strong>
            Curiosity angle
          </strong>
        </label>

        <textarea
          name="curiosity_angle"
          rows="4"
        >{esc(analysis["CURIOSITY ANGLE"])}</textarea>

        <br><br>

        <label>
          <strong>
            Target length
          </strong>
        </label>

        <input
          name="length_minutes"
          value="{length}"
          type="number"
          min="1"
          max="60"
        >

        <br><br>

        <label>
          <strong>
            Strategy map
          </strong>
        </label>

        <p class="muted">
          This is editable. Remove strategies you don't want.
          Add or modify them if necessary.
        </p>

        <textarea
          name="strategy_map"
          rows="20"
        >{esc(strategy_text)}</textarea>

        <br><br>

        <button type="submit">
          Approve &amp; Plan Script
        </button>

      </form>

      <p>
        <a href="/">
          &larr; Start over
        </a>
      </p>
    """

    return page(body_html)


# =============================================================================
# STRATEGY MAP → OUTLINE
# =============================================================================

@app.post(
    "/strategy-map",
    response_class=HTMLResponse,
)
async def strategy_map(
    topic: str = Form(...),
    audience: str = Form(""),
    objective: str = Form(""),
    curiosity_angle: str = Form(""),
    length_minutes: str = Form("10"),
    strategy_map: str = Form(...),
    input_type: str = Form("topic"),
    source_context: str = Form(""),
    claim_register: str = Form("{}"),
    creative_direction: str = Form(""),
):

    if not GEMINI_API_KEY:

        return page(
            "<p class='critical'>"
            "Missing GEMINI_API_KEY."
            "</p>"
        )

    try:

        length = int(
            float(length_minutes)
        )

    except (ValueError, TypeError):

        length = 10

    if length < 1:
        length = 1

    if length > 60:
        length = 60

    word_target = int(
        length * WORDS_PER_MINUTE
    )

    try:

        claim_register_data = json.loads(
            claim_register or "{}"
        )

        claims = (
            claim_register_data.get("claims", [])
            if isinstance(claim_register_data, dict)
            else []
        )

        control_plane_module.build_claim_register(
            claims
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Claim Register validation failed:
              {esc(exc)}
            </p>
            """
        )

    governance_text = get_governance_text(
        strategy_map
    )

    rehook_text = "\n".join(
        f"- {desc}"
        for desc in REHOOK_TECHNIQUES.values()
    )

    prompt = OUTLINE_PROMPT_TEMPLATE.format(
        topic=topic,
        creative_direction=creative_direction,
        source_context=source_context,
        length_minutes=length,
        word_target=word_target,
        strategy_map=strategy_map,
        claim_register=claim_register,
        governance=governance_text,
        structure=STRUCTURE_TEMPLATE,
        hook_framework=HOOK_FRAMEWORK,
        rehook_techniques=rehook_text,
    )

    try:

        outline_text = call_gemini(
            prompt
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Outline generation failed:
              {esc(exc)}
            </p>
            """
        )

    body_html = f"""
      <h3>
        2. Review / Edit Script Plan
      </h3>

      <div class="card">

        <p class="muted">
          This is the approved architecture for the script.
          Edit it before the prose is generated.
        </p>

        <form
          method="post"
          action="/script"
        >

          <input
            type="hidden"
            name="topic"
            value="{esc(topic)}"
          >

          <input
            type="hidden"
            name="audience"
            value="{esc(audience)}"
          >

          <input
            type="hidden"
            name="objective"
            value="{esc(objective)}"
          >

          <input
            type="hidden"
            name="curiosity_angle"
            value="{esc(curiosity_angle)}"
          >

          <input
            type="hidden"
            name="input_type"
            value="{esc(input_type)}"
          >

          <input
            type="hidden"
            name="source_context"
            value="{esc(source_context)}"
          >

          <input
            type="hidden"
            name="claim_register"
            value="{esc(claim_register)}"
          >

          <input
            type="hidden"
            name="creative_direction"
            value="{esc(creative_direction)}"
          >

          <input
            type="hidden"
            name="length_minutes"
            value="{length}"
          >

          <input
            type="hidden"
            name="strategy_map"
            value="{esc(strategy_map)}"
          >

          <textarea
            name="outline"
            rows="28"
            required
          >{esc(outline_text)}</textarea>

          <br><br>

          <button type="submit">
            Generate Script
          </button>

        </form>

      </div>

      <p>
        <a href="/">
          &larr; Start over
        </a>
      </p>
    """

    return page(body_html)


# =============================================================================
# SCRIPT GENERATION
# =============================================================================

@app.post(
    "/script",
    response_class=HTMLResponse,
)
async def script(
    topic: str = Form(...),
    audience: str = Form(""),
    objective: str = Form(""),
    curiosity_angle: str = Form(""),
    length_minutes: str = Form("10"),
    strategy_map: str = Form(...),
    outline: str = Form(...),
    input_type: str = Form("topic"),
    source_context: str = Form(""),
    claim_register: str = Form("{}"),
    creative_direction: str = Form(""),
):

    if not GEMINI_API_KEY:

        return page(
            "<p class='critical'>"
            "Missing GEMINI_API_KEY."
            "</p>"
        )

    try:

        length = int(
            float(length_minutes)
        )

    except (ValueError, TypeError):

        length = 10

    if length < 1:
        length = 1

    if length > 60:
        length = 60

    word_target = int(
        length * WORDS_PER_MINUTE
    )

    try:

        claim_register_data = json.loads(
            claim_register or "{}"
        )

        claims = (
            claim_register_data.get("claims", [])
            if isinstance(claim_register_data, dict)
            else []
        )

        control_plane_module.build_claim_register(
            claims
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Claim Register validation failed:
              {esc(exc)}
            </p>
            """
        )

    governance_text = get_governance_text(
        strategy_map
    )

    prompt = SCRIPT_PROMPT_TEMPLATE.format(
        topic=topic,
        creative_direction=creative_direction,
        source_context=source_context,
        length_minutes=length,
        word_target=word_target,
        strategy_map=strategy_map,
        outline=outline,
        claim_register=claim_register,
        governance=governance_text,
        humanizing_guidelines=HUMANIZING_GUIDELINES,
        banned_phrases=", ".join(
            BANNED_PHRASES
        ),
        pacing_example=PACING_EXAMPLE,
    )

    try:

        script_text = call_gemini(
            prompt
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Script generation failed:
              {esc(exc)}
            </p>
            """
        )

    # -------------------------------------------------------------------------
    # V2 VALIDATION
    # -------------------------------------------------------------------------

    try:

        validation = validate_generated_script(
            script_text=script_text,
            topic=topic,
            outline=outline,
            strategy_map=strategy_map,
            length_minutes=length,
            claim_register=claim_register,
        )

    except Exception as exc:

        return page(
            f"""
            <div class="critical">

              <h3>
                Validation could not run
              </h3>

              <p>
                {esc(exc)}
              </p>

              <p>
                The script has NOT been silently passed through.
                Fix the validator integration before relying on V2.
              </p>

            </div>
            """
        )

    status = validation_status(
        validation
    )

    validation_text = result_to_text(
        validation
    )

    if status == "CRITICAL":

        body_html = f"""
          <h3>
            3. Script Validation
          </h3>

          <div class="critical">

            <h3>
              CRITICAL
            </h3>

            <p>
              The generated script contains one or more issues
              that should be reviewed before it is accepted.
            </p>

          </div>

          <div class="card">

            <pre style="
              white-space:pre-wrap;
              font-family:sans-serif;
            ">{esc(validation_text)}</pre>

          </div>

          <h3>
            Generated Script
          </h3>

          <form
            method="post"
            action="/accept-script"
          >

            <input
              type="hidden"
              name="topic"
              value="{esc(topic)}"
            >

            <textarea
              name="script_text"
              rows="30"
            >{esc(script_text)}</textarea>

            <br><br>

            <button type="submit">
              I Reviewed It — Continue
            </button>

          </form>

          <p>
            <a href="/">
              &larr; Start over
            </a>
          </p>
        """

        return page(body_html)

    body_html = f"""
      <h3>
        3. Script Validation
      </h3>

      <div class="pass">

        <h3>
          PASS
        </h3>

        <p>
          The validator did not identify a critical
          blocking failure.
        </p>

      </div>

      <div class="card">

        <h3>
          Validation report
        </h3>

        <pre style="
          white-space:pre-wrap;
          font-family:sans-serif;
        ">{esc(validation_text)}</pre>

      </div>

      <h3>
        Review / Edit Final Script
      </h3>

      <form
        method="post"
        action="/voiceover"
      >

        <input
          type="hidden"
          name="topic"
          value="{esc(topic)}"
        >

        <textarea
          name="script_text"
          rows="30"
          required
        >{esc(script_text)}</textarea>

        <br><br>

        <label>
          <strong>
            Voice
          </strong>
        </label>

        <select name="voice">

          {"".join(
              f'<option value="{esc(v)}">'
              f'{esc(label)}'
              f'</option>'
              for v, label in VOICES
          )}

        </select>

        <br><br>

        <button type="submit">
          Generate Voiceover
        </button>

      </form>

      <p>
        <a href="/">
          &larr; Start over
        </a>
      </p>
    """

    return page(body_html)


# =============================================================================
# CRITICAL VALIDATION OVERRIDE
# =============================================================================

@app.post(
    "/accept-script",
    response_class=HTMLResponse,
)
async def accept_script(
    topic: str = Form(...),
    script_text: str = Form(...),
):

    voice_options = "".join(
        f'<option value="{esc(v)}">'
        f'{esc(label)}'
        f'</option>'
        for v, label in VOICES
    )

    body_html = f"""
      <h3>
        Final Script Review
      </h3>

      <p class="warning">
        You chose to continue after reviewing a critical
        validation report.

        The system has not silently modified your script.
      </p>

      <form
        method="post"
        action="/voiceover"
      >

        <input
          type="hidden"
          name="topic"
          value="{esc(topic)}"
        >

        <textarea
          name="script_text"
          rows="30"
          required
        >{esc(script_text)}</textarea>

        <br><br>

        <label>
          <strong>
            Voice
          </strong>
        </label>

        <select name="voice">

          {voice_options}

        </select>

        <br><br>

        <button type="submit">
          Generate Voiceover
        </button>

      </form>

      <p>
        <a href="/">
          &larr; Start over
        </a>
      </p>
    """

    return page(body_html)


# =============================================================================
# VIDEO INSPIRATION
# =============================================================================

@app.post(
    "/video-inspiration",
    response_class=HTMLResponse,
)
async def video_inspiration(
    video_url: str = Form(...),
):

    if not GEMINI_API_KEY:

        return page(
            "<p class='critical'>"
            "Missing GEMINI_API_KEY."
            "</p>"
        )

    if not YOUTUBE_API_KEY:

        return page(
            "<p class='critical'>"
            "Missing YOUTUBE_API_KEY."
            "</p>"
        )

    try:

        video_id = extract_video_id(
            video_url
        )

        metadata = get_video_metadata(
            video_id,
            YOUTUBE_API_KEY,
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Could not read video:
              {esc(exc)}
            </p>
            """
        )

    title_frames_text = "\n".join(
        f"- {desc}"
        for desc in TITLE_FRAMES.values()
    )

    prompt = (
        VIDEO_INSPIRATION_PROMPT_TEMPLATE
        .format(
            source_title=metadata["title"],
            source_description=metadata[
                "description"
            ][:500],
            source_tags=", ".join(
                metadata["tags"][:15]
            ),
            title_frames=title_frames_text,
            frame_stacking_note=FRAME_STACKING_NOTE,
        )
    )

    try:

        raw = call_gemini(
            prompt
        )

    except Exception as exc:

        return page(
            f"""
            <p class='critical'>
              Suggestion failed:
              {esc(exc)}
            </p>
            """
        )

    title_match = re.search(
        r"TITLE:\s*(.+)",
        raw,
        re.IGNORECASE,
    )

    why_match = re.search(
        r"WHY:\s*(.+)",
        raw,
        re.IGNORECASE | re.DOTALL,
    )

    suggested_title = (
        title_match.group(1).strip()
        if title_match
        else raw.strip()
    )

    why = (
        why_match.group(1).strip()
        if why_match
        else ""
    )

    suggested_title = clean_title_text(
        suggested_title
    )

    body_html = f"""
      <h3>
        Inspired Video Angle
      </h3>

      <div class="card">

        <p>
          <strong>
            Source:
          </strong>

          {esc(metadata["title"])}
        </p>

        <p>
          This is inspiration only.

          The new idea should not copy
          the source video's wording or structure.
        </p>

      </div>

      <form
        method="post"
        action="/analyze"
      >

        <input
          type="hidden"
          name="input_type"
          value="topic"
        >

        <input
          type="hidden"
          name="topic"
          value="{esc(suggested_title)}"
        >

        <label>
          <strong>
            Suggested title / topic
          </strong>
        </label>

        <input
          name="topic"
          value="{esc(suggested_title)}"
          required
        >

        <br><br>

        <div class="card">

          <strong>
            Why this angle
          </strong>

          <p>
            {esc(why)}
          </p>

        </div>

        <label>
          <strong>
            Target length
          </strong>
        </label>

        <input
          name="length_minutes"
          value="10"
          type="number"
          min="1"
          max="60"
        >

        <br><br>

        <button type="submit">
          Analyze This Angle
        </button>

      </form>

      <p>
        <a href="/">
          &larr; Start over
        </a>
      </p>
    """

    return page(body_html)


# =============================================================================
# VOICEOVER
# =============================================================================

async def generate_voiceover(
    script_text: str,
    voice: str,
    filepath: str,
):

    communicate = edge_tts.Communicate(
        script_text,
        voice,
    )

    await communicate.save(
        filepath
    )


@app.post(
    "/voiceover",
    response_class=HTMLResponse,
)
async def voiceover(
    script_text: str = Form(...),
    voice: str = Form("en-US-GuyNeural"),
    topic: str = Form(""),
):

    safe_name = (
        re.sub(
            r"[^a-zA-Z0-9]+",
            "-",
            script_text[:30].lower(),
        )[:30]
        or "voiceover"
    )

    filename = (
        f"{safe_name}-"
        f"{int(time.time())}.mp3"
    )

    filepath = os.path.join(
        AUDIO_DIR,
        filename,
    )

    try:

        await generate_voiceover(
            script_text,
            voice,
            filepath,
        )

    except Exception as exc:

        body_html = f"""
          <p class="critical">

            Voiceover generation failed:

            {esc(exc)}

          </p>

          <h3>
            Script
          </h3>

          <textarea rows="30">
{esc(script_text)}
          </textarea>

          <p>
            <a href="/">
              &larr; Start over
            </a>
          </p>
        """

        return page(
            body_html
        )

    body_html = f"""
      <h3>
        Ren Media V2 — Complete
      </h3>

      <h3>
        Final Script
      </h3>

      <textarea rows="30">
{esc(script_text)}
      </textarea>

      <h3>
        Voiceover
      </h3>

      <audio
        controls
        src="/audio/{esc(filename)}"
        style="width:100%;"
      ></audio>

      <br><br>

      <a
        href="/audio/{esc(filename)}"
        download
      >
        Download voiceover (.mp3)
      </a>

      <p>
        <a href="/">
          &larr; Create another video
        </a>
      </p>
    """

    return page(
        body_html
    )
