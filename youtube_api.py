import re
import requests

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def extract_video_id(url: str) -> str:
    """Pull the video ID out of common YouTube URL formats."""
    patterns = [
        r"(?:v=|/shorts/|youtu\.be/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not find a video ID in that URL.")


def get_video_metadata(video_id: str, api_key: str) -> dict:
    """
    Fetch a video's public title/description/tags. This is a cheap call
    (1 quota unit) -- safe to use often. Only metadata is pulled, never
    the transcript, so this stays inspiration-only, not content-copying.
    """
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/videos",
        params={"part": "snippet", "id": video_id, "key": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise ValueError("No video found for that link.")
    snippet = items[0]["snippet"]
    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "tags": snippet.get("tags", []),
    }


def search_current_titles(query: str, api_key: str, max_results: int = 5) -> list:
    """
    Search YouTube for what's currently ranking on a topic. This is the
    EXPENSIVE call -- 100 quota units per search, against a 10,000/day
    free-tier budget, so roughly 100 of these are usable per day.
    Raises QuotaExceededError specifically so the caller can fall back
    gracefully instead of crashing.
    """
    search_resp = requests.get(
        f"{YOUTUBE_API_BASE}/search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "maxResults": max_results,
            "key": api_key,
        },
        timeout=30,
    )
    if search_resp.status_code == 403 and "quotaExceeded" in search_resp.text:
        raise QuotaExceededError("YouTube API daily search quota has been used up.")
    search_resp.raise_for_status()

    items = search_resp.json().get("items", [])
    video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]
    if not video_ids:
        return []

    stats_resp = requests.get(
        f"{YOUTUBE_API_BASE}/videos",
        params={"part": "snippet,statistics", "id": ",".join(video_ids), "key": api_key},
        timeout=30,
    )
    stats_resp.raise_for_status()

    results = []
    for item in stats_resp.json().get("items", []):
        results.append({
            "title": item["snippet"].get("title", ""),
            "published_at": item["snippet"].get("publishedAt", ""),
            "view_count": item.get("statistics", {}).get("viewCount", "unknown"),
        })
    return results


class QuotaExceededError(Exception):
    pass
