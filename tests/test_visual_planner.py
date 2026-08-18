import json

import pytest

from visual_planner import build_visual_plan, build_visual_plan_prompt, parse_visual_plan


def valid_plan():
    return {
        "visual_plan": [
            {
                "beat_id": 1,
                "narration_summary": "A couple struggles to communicate.",
                "visual_purpose": "Make the conflict immediately understandable.",
                "visual_type": "stock_video",
                "shot": "Two adults sitting apart during a tense conversation.",
                "mood": "tense",
                "search_queries": ["couple arguing", "tense couple conversation", "relationship conflict"],
                "duration_seconds": 7,
                "priority": "high",
            }
        ]
    }


def test_visual_plan_prompt_contains_script_and_topic():
    prompt = build_visual_plan_prompt("A couple keeps misunderstanding each other.", "Communication")
    assert "A couple keeps misunderstanding each other." in prompt
    assert "Communication" in prompt
    assert "search_queries" in prompt


def test_parse_visual_plan_accepts_valid_json():
    result = parse_visual_plan(json.dumps(valid_plan()))
    assert result["visual_plan"][0]["beat_id"] == 1
    assert result["visual_plan"][0]["visual_type"] == "stock_video"


def test_parse_visual_plan_rejects_missing_required_field():
    plan = valid_plan()
    del plan["visual_plan"][0]["shot"]
    with pytest.raises(ValueError, match="required fields"):
        parse_visual_plan(json.dumps(plan))


def test_parse_visual_plan_rejects_duplicate_ids():
    plan = valid_plan()
    second = dict(plan["visual_plan"][0])
    plan["visual_plan"].append(second)
    with pytest.raises(ValueError, match="unique"):
        parse_visual_plan(json.dumps(plan))


def test_parse_visual_plan_rejects_invalid_visual_type():
    plan = valid_plan()
    plan["visual_plan"][0]["visual_type"] = "random_clip"
    with pytest.raises(ValueError, match="unsupported visual_type"):
        parse_visual_plan(json.dumps(plan))


def test_parse_visual_plan_rejects_non_positive_duration():
    plan = valid_plan()
    plan["visual_plan"][0]["duration_seconds"] = 0
    with pytest.raises(ValueError, match="positive"):
        parse_visual_plan(json.dumps(plan))


def test_build_visual_plan_requires_script():
    with pytest.raises(ValueError, match="Script is required"):
        build_visual_plan("", "Topic", lambda prompt: "{}")


def test_build_visual_plan_passes_prompt_to_gemini():
    captured = {}

    def fake_gemini(prompt):
        captured["prompt"] = prompt
        return json.dumps(valid_plan())

    result = build_visual_plan("A couple struggles to communicate.", "Communication", fake_gemini)
    assert result["visual_plan"]
    assert "A couple struggles to communicate." in captured["prompt"]
