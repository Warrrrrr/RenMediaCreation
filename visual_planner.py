import json
import re


VISUAL_PLAN_PROMPT = """
You are the visual-planning layer of a professional YouTube production system.

Convert the approved spoken script into a practical visual plan.

The visual plan is NOT a video. Do not source footage and do not write narration.
Do not invent factual evidence, people, events, locations, statistics, or real-world
scenes that are not supported by the script.

TOPIC:
{topic}

SCRIPT:
{script}

Create a sequence of visual beats that covers the full script. Group narration into
meaningful visual beats rather than creating one beat per sentence.

For each beat return:
- beat_id: sequential integer
- narration_summary: concise summary of the narration covered
- visual_purpose: what the visual is helping the viewer understand or feel
- visual_type: stock_video|photo|graphic|text|screen|abstract
- shot: concrete shot description
- mood: concise mood
- search_queries: 3 to 5 concrete stock-search queries
- duration_seconds: estimated duration for this beat
- priority: high|medium|low

Rules:
- Prefer visuals that directly clarify the narration.
- Use concrete, searchable descriptions rather than abstract keywords.
- Use stock_video when real-world motion naturally supports the narration.
- Use graphic or text when a concept, number, comparison, or evidence point is better shown explicitly.
- Use abstract footage only when a literal visual would mislead or be impossible to source.
- Do not invent a real person, study scene, medical event, or historical event merely to make a visual interesting.
- Do not imply that stock footage depicts the real people or events discussed in the narration.
- Avoid repetitive shots and generic filler.
- Search queries must describe what should actually appear in the footage, not internal writing terminology.
- The total duration should approximately cover the script.

Return valid JSON only using exactly:
{{
  "visual_plan": [
    {{
      "beat_id": 1,
      "narration_summary": "",
      "visual_purpose": "",
      "visual_type": "stock_video",
      "shot": "",
      "mood": "",
      "search_queries": [],
      "duration_seconds": 6,
      "priority": "high"
    }}
  ]
}}
"""


def build_visual_plan_prompt(script, topic=""):
    return VISUAL_PLAN_PROMPT.format(
        topic=str(topic or "").strip(),
        script=str(script or "").strip(),
    )


def parse_visual_plan(raw_text):
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Visual planner returned invalid JSON.")
        result = json.loads(match.group(0))

    if not isinstance(result, dict) or not isinstance(result.get("visual_plan"), list):
        raise ValueError("Visual plan must contain a visual_plan list.")

    required = {
        "beat_id",
        "narration_summary",
        "visual_purpose",
        "visual_type",
        "shot",
        "mood",
        "search_queries",
        "duration_seconds",
        "priority",
    }
    allowed_types = {"stock_video", "photo", "graphic", "text", "screen", "abstract"}
    allowed_priorities = {"high", "medium", "low"}
    seen = set()

    for beat in result["visual_plan"]:
        if not isinstance(beat, dict) or not required.issubset(beat):
            raise ValueError("Every visual beat must contain all required fields.")
        beat_id = beat["beat_id"]
        if beat_id in seen:
            raise ValueError("Visual beat IDs must be unique.")
        seen.add(beat_id)
        if beat["visual_type"] not in allowed_types:
            raise ValueError("Visual beat has an unsupported visual_type.")
        if beat["priority"] not in allowed_priorities:
            raise ValueError("Visual beat has an unsupported priority.")
        if not isinstance(beat["search_queries"], list):
            raise ValueError("search_queries must be a list.")
        if not isinstance(beat["duration_seconds"], (int, float)) or beat["duration_seconds"] <= 0:
            raise ValueError("duration_seconds must be positive.")

    return result


def build_visual_plan(script, topic, call_gemini):
    if not str(script or "").strip():
        raise ValueError("Script is required for visual planning.")
    raw = call_gemini(build_visual_plan_prompt(script, topic))
    return parse_visual_plan(raw)
