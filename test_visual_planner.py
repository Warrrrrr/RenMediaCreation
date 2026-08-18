import json

import pytest

from visual_planner import parse_visual_plan, build_visual_plan_prompt


def valid_plan():
    return {
        "visual_plan": [
            {
                "beat_id": 1,
                "narration_summary": "A couple argues.",
                "visual_purpose": "Make conflict immediately understandable.",
                "visual_type": "stock_video",
                "shot": "Two adults having a tense conversation at home.",
                "mood": "tense",
                "search_queries": ["couple arguing at home", "tense couple conversation", "relationship conflict"],
                "duration_seconds": 6,
                "priority": "high",
            }
        ]
    }


def test_visual_plan_requires_complete_beats():
    payload = valid_plan()
    del payload["visual_plan"][0]["shot"]
    with pytest.raises(ValueError):
        parse_visual_plan(json.dumps(payload))


def test_visual_plan_rejects_duplicate_ids():
    payload = valid_plan()
    payload["visual_plan"].append(dict(payload["visual_plan"][0]))
    with pytest.raises(ValueError):
        parse_visual_plan(json.dumps(payload))


def test_visual_plan_rejects_invalid_type():
    payload = valid_plan()
    payload["visual_plan"][0]["visual_type"] = "made_up_type"
    with pytest.raises(ValueError):
        parse_visual_plan(json.dumps(payload))


def test_prompt_contains_script_and_search_rules():
    prompt = build_visual_plan_prompt("The couple sits in silence.", "Relationship conflict")
    assert "The couple sits in silence." in prompt
    assert "search queries" in prompt
    assert "Do not invent a real person" in prompt
