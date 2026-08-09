import os
import re
import time
import html
import requests
import edge_tts
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from psychology import PSYCHOLOGY_TECHNIQUES
from hooks_and_titling import TITLE_FRAMES, FRAME_STACKING_NOTE, HOOK_FRAMEWORK, REHOOK_TECHNIQUES
from humanizing import BANNED_PHRASES, HUMANIZING_GUIDELINES, PACING_EXAMPLE
from youtube_api import extract_video_id, get_video_metadata, search_current_titles, QuotaExceededError

app = FastAPI()

AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"

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
# VIDEO STRUCTURE
# =============================================================================
STRUCTURE_TEMPLATE = """1. Cold Open / Hook (roughly first 5% of runtime) -- create a curiosity gap in the first two lines, following the hook framework provided.
2. Setup / Exposition (next ~10% of runtime) -- validate the viewer's current experience or struggle before introducing anything new, so they feel seen and stay with you.
3. Four to six escalating Acts/Sections -- each section builds on the previous one using "But" / "Therefore" causal logic, not "and then". Pacing should be tighter (shorter beats, quicker turns) in the first third of the video, and more stabilized/explanatory in the middle third.
4. Rehooks -- place a rehook (see rehook techniques provided) roughly every 2-3 minutes of runtime, especially right after any question or mini-stakes resolves. Never let a section end on a flat, comfortable note.
5. Climax -- where the macro open loop gets resolved.
6. Payoff / Resolution -- the satisfying takeaway. This video should feel self-contained and fully resolved -- do not tease or open a loop for a future video.
7. Outro / CTA -- a natural subscribe ask."""

OUTLINE_PROMPT_TEMPLATE = """You are a professional long-form YouTube scriptwriter and story architect. Plan the STRUCTURE for a video on this topic: "{topic}".

Target spoken length: approximately {length_minutes} minutes (about {word_target} words of narration).

Output a structured beat sheet, NOT prose narration. Use this exact format, one beat per line:

[SECTION NAME] -- Purpose/content of this beat (1-3 sentences describing what happens and which technique it uses)

VIDEO STRUCTURE TO FOLLOW:
{structure}

HOOK FRAMEWORK (for the opening beat):
{hook_framework}

REHOOK TECHNIQUES (use a mix of these across the video, not just one repeated):
{rehook_techniques}

PSYCHOLOGICAL / STORYTELLING TECHNIQUES TO WEAVE IN (apply each one at the beat where it fits best):
{techniques}

These frameworks are inspiration and a foundation, not a rigid cage -- you have creative freedom to combine, adapt, or invent beyond them where it makes the video genuinely better, as long as the core structure and rules above are respected.

Rules:
- Do not write any actual narration text yet -- structural plan only.
- Do not invent or reference specific named studies, researchers, or statistics -- describe psychological techniques generically without fabricating sources.
- Keep each beat description concise.
"""

SCRIPT_PROMPT_TEMPLATE = """You are a professional long-form YouTube scriptwriter. Expand the following APPROVED beat outline into a complete voiceover narration script for a video on: "{topic}".

Target spoken length: approximately {length_minutes} minutes (about {word_target} words).

APPROVED OUTLINE:
{outline}

WRITING STYLE GUIDELINES:
{humanizing_guidelines}

NEVER use any of these words/phrases (they are recognizable AI writing tells):
{banned_phrases}

{pacing_example}

Write the full narration following this outline's structure and beats, in order. Rules:
- Output ONLY the spoken narration text a narrator would read aloud -- no section headers, timestamps, labels, or stage directions.
- Never include bracketed markers like [pause] or [beat] in the text -- edge-tts will read them aloud literally since it cannot process custom pause markup. Use punctuation (periods, ellipses, em dashes, short sentences) to create pacing and pauses instead.
- Write it as one continuous piece, not a list of separate segments.
- Use "But" and "therefore" (or natural equivalents) to connect ideas causally rather than "and then".
- NEVER use story-structure or technique jargon inside the narration itself -- words like "open loop", "macro loop", "climax", "act", "beat", "pattern interrupt", "rehook", or "foot-in-the-door" must never be spoken by the narrator. Execute the technique; don't name it.
- Vary sentence pacing concretely: any sentence longer than about 25 words must be followed by one under about 10 words. Do not let more than two long sentences in a row pass without a short one breaking the rhythm.
- Do not invent or cite specific named studies, researchers, or statistics -- use soft, generic attribution only for well-established ideas (e.g. "many psychologists point to...") and never fabricate a source.
- Follow the outline's placement of the open loop resolution, the audience foot-in-the-door moment, the rehooks, and the CTA exactly as planned.
- You have creative freedom in wording and phrasing -- the frameworks above are inspiration for technique and rhythm, not scripts to imitate word-for-word.
"""

TITLE_CHECK_PROMPT_TEMPLATE = """You are a YouTube title strategist. The creator wants to make a video about: "{topic}".

{context_block}

VIRAL TITLE FRAMES (for reference and inspiration -- stack 2-4 of these together for the strongest titles, but feel free to go beyond them if a better title occurs to you):
{title_frames}

{frame_stacking_note}

Suggest ONE improved, currently-relevant title for this video. Then in one short paragraph, explain why this title works right now.

Format your answer exactly as:
TITLE: <the suggested title>
WHY: <short explanation>
"""

VIDEO_INSPIRATION_PROMPT_TEMPLATE = """You are a YouTube content strategist. Another creator published a video with this public metadata:

Title: {source_title}
Description: {source_description}
Tags: {source_tags}

Using this ONLY as inspiration for the topic/angle (never copy its wording, claims, or structure), suggest an original title and topic for a NEW, different video the user could make on a related angle.

VIRAL TITLE FRAMES (for reference and inspiration -- stack 2-4 of these together for the strongest titles, but feel free to go beyond them if a better title occurs to you):
{title_frames}

{frame_stacking_note}

Format your answer exactly as:
TITLE: <the suggested title>
WHY: <short explanation of the angle and how it differs from the source>
"""


def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(GEMINI_URL, headers=headers, json=body, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def page(body_html: str) -> str:
    return f"""
    <html>
    <head>
      <title>Script + Voiceover Generator</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="font-family:sans-serif; max-width:600px; margin:20px auto; padding:0 12px;">
      <h2>Script + Voiceover Generator</h2>
      {body_html}
    </body>
    </html>
    """


def esc(text: str) -> str:
    return html.escape(text or "")


def outline_start_form(topic: str) -> str:
    return f"""
      <h3>Suggested topic/title</h3>
      <p>Edit if needed, then continue to the outline stage.</p>
      <form method="post" action="/outline">
        <input name="topic" value="{esc(topic)}" style="width:100%;padding:8px;font-size:16px;" required><br><br>
        <label>Target length (minutes)</label><br>
        <input name="length_minutes" value="10" style="width:100%;padding:8px;font-size:16px;"><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate Outline</button>
      </form>
      <p><a href="/">&larr; Start over</a></p>
    """


def parse_title_suggestion(raw_text: str) -> tuple:
    title_match = re.search(r"TITLE:\s*(.+)", raw_text)
    why_match = re.search(r"WHY:\s*(.+)", raw_text, re.DOTALL)
    title = title_match.group(1).strip() if title_match else raw_text.strip()
    why = why_match.group(1).strip() if why_match else ""
    return title, why


@app.get("/", response_class=HTMLResponse)
async def home():
    body_html = """
      <h3>Option 1 -- Start from a topic (checks what's currently working)</h3>
      <form method="post" action="/check-title">
        <input name="topic" placeholder="e.g. why women lose interest fast" style="width:100%;padding:8px;font-size:16px;" required><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Check Title</button>
      </form>
      <br>
      <h3>Option 2 -- Start from a YouTube video (as inspiration only)</h3>
      <form method="post" action="/video-inspiration">
        <input name="video_url" placeholder="https://youtube.com/watch?v=..." style="width:100%;padding:8px;font-size:16px;" required><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Get Suggested Angle</button>
      </form>
    """
    return page(body_html)


@app.post("/check-title", response_class=HTMLResponse)
async def check_title(topic: str = Form(...)):
    if not GEMINI_API_KEY:
        return page("<p style='color:#c0392b;'>Missing GEMINI_API_KEY.</p>")

    context_block = ""
    quota_note = ""

    if YOUTUBE_API_KEY:
        try:
            results = search_current_titles(topic, YOUTUBE_API_KEY, max_results=5)
            if results:
                lines = "\n".join(
                    f"- \"{r['title']}\" ({r['view_count']} views, published {r['published_at'][:10]})"
                    for r in results
                )
                context_block = f"Here is what's currently ranking on this topic on YouTube:\n{lines}"
            else:
                context_block = "No current search data was found for this topic -- use general best practice instead."
        except QuotaExceededError:
            context_block = "No live search data is available right now (daily search budget used up) -- use general best practice instead."
            quota_note = "<p><em>Note: today's search-based check budget is used up, so this suggestion is based on general best practice rather than live data.</em></p>"
    else:
        context_block = "No YouTube API key is configured -- use general best practice instead."

    title_frames_text = "\n".join(f"- {desc}" for desc in TITLE_FRAMES.values())
    prompt = TITLE_CHECK_PROMPT_TEMPLATE.format(
        topic=topic,
        context_block=context_block,
        title_frames=title_frames_text,
        frame_stacking_note=FRAME_STACKING_NOTE,
    )

    try:
        raw = call_gemini(prompt)
    except Exception as e:
        return page(f"<p style='color:#c0392b;'>Title check failed: {esc(str(e))}</p>")

    suggested_title, why = parse_title_suggestion(raw)

    body_html = f"""
      <h3>Title suggestion</h3>
      {quota_note}
      <p><strong>{esc(suggested_title)}</strong></p>
      <p>{esc(why)}</p>
      {outline_start_form(suggested_title)}
    """
    return page(body_html)


@app.post("/video-inspiration", response_class=HTMLResponse)
async def video_inspiration(video_url: str = Form(...)):
    if not GEMINI_API_KEY:
        return page("<p style='color:#c0392b;'>Missing GEMINI_API_KEY.</p>")
    if not YOUTUBE_API_KEY:
        return page("<p style='color:#c0392b;'>Missing YOUTUBE_API_KEY -- add it in Render's Environment Variables, then redeploy.</p>")

    try:
        video_id = extract_video_id(video_url)
        metadata = get_video_metadata(video_id, YOUTUBE_API_KEY)
    except Exception as e:
        return page(f"<p style='color:#c0392b;'>Could not read that video: {esc(str(e))}</p>")

    title_frames_text = "\n".join(f"- {desc}" for desc in TITLE_FRAMES.values())
    prompt = VIDEO_INSPIRATION_PROMPT_TEMPLATE.format(
        source_title=metadata["title"],
        source_description=metadata["description"][:500],
        source_tags=", ".join(metadata["tags"][:15]),
        title_frames=title_frames_text,
        frame_stacking_note=FRAME_STACKING_NOTE,
    )

    try:
        raw = call_gemini(prompt)
    except Exception as e:
        return page(f"<p style='color:#c0392b;'>Suggestion failed: {esc(str(e))}</p>")

    suggested_title, why = parse_title_suggestion(raw)

    body_html = f"""
      <h3>Suggested angle (inspired by, not copied from, the source video)</h3>
      <p><em>Source video: {esc(metadata['title'])}</em></p>
      <p><strong>{esc(suggested_title)}</strong></p>
      <p>{esc(why)}</p>
      {outline_start_form(suggested_title)}
    """
    return page(body_html)


@app.post("/outline", response_class=HTMLResponse)
async def outline(topic: str = Form(...), length_minutes: str = Form("10")):
    if not GEMINI_API_KEY:
        return page("<p style='color:#c0392b;'>Missing GEMINI_API_KEY -- add it in Render's Environment Variables, then redeploy.</p>")

    word_target = int(float(length_minutes) * WORDS_PER_MINUTE)
    techniques_text = "\n\n".join(
        f"- {t['name']}: {t['explanation']} Example: {t['example']}"
        for t in PSYCHOLOGY_TECHNIQUES.values()
    )
    rehook_text = "\n".join(f"- {desc}" for desc in REHOOK_TECHNIQUES.values())
    prompt = OUTLINE_PROMPT_TEMPLATE.format(
        topic=topic,
        length_minutes=length_minutes,
        word_target=word_target,
        structure=STRUCTURE_TEMPLATE,
        hook_framework=HOOK_FRAMEWORK,
        rehook_techniques=rehook_text,
        techniques=techniques_text,
    )

    try:
        outline_text = call_gemini(prompt)
    except Exception as e:
        return page(f"<p style='color:#c0392b;'>Outline generation failed: {esc(str(e))}</p>")

    body_html = f"""
      <h3>Review / edit the outline</h3>
      <p>Edit anything below, then generate the full script from this outline.</p>
      <form method="post" action="/script">
        <input type="hidden" name="topic" value="{esc(topic)}">
        <input type="hidden" name="length_minutes" value="{esc(length_minutes)}">
        <textarea name="outline" rows="20" style="width:100%;font-size:15px;">{esc(outline_text)}</textarea><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate Full Script</button>
      </form>
      <p><a href="/">&larr; Start over</a></p>
    """
    return page(body_html)


@app.post("/script", response_class=HTMLResponse)
async def script(topic: str = Form(...), length_minutes: str = Form("10"), outline: str = Form(...)):
    if not GEMINI_API_KEY:
        return page("<p style='color:#c0392b;'>Missing GEMINI_API_KEY -- add it in Render's Environment Variables, then redeploy.</p>")

    word_target = int(float(length_minutes) * WORDS_PER_MINUTE)
    prompt = SCRIPT_PROMPT_TEMPLATE.format(
        topic=topic,
        length_minutes=length_minutes,
        word_target=word_target,
        outline=outline,
        humanizing_guidelines=HUMANIZING_GUIDELINES,
        banned_phrases=", ".join(BANNED_PHRASES),
        pacing_example=PACING_EXAMPLE,
    )

    try:
        script_text = call_gemini(prompt)
    except Exception as e:
        return page(f"<p style='color:#c0392b;'>Script generation failed: {esc(str(e))}</p>")

    voice_options = "".join(f'<option value="{v}">{label}</option>' for v, label in VOICES)
    body_html = f"""
      <h3>Review / edit the full script</h3>
      <form method="post" action="/voiceover">
        <textarea name="script_text" rows="22" style="width:100%;font-size:15px;">{esc(script_text)}</textarea><br><br>
        <label>Voice</label><br>
        <select name="voice" style="width:100%;padding:8px;font-size:16px;">
          {voice_options}
        </select><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate Voiceover</button>
      </form>
      <p><a href="/">&larr; Start over</a></p>
    """
    return page(body_html)


async def generate_voiceover(script_text: str, voice: str, filepath: str):
    communicate = edge_tts.Communicate(script_text, voice)
    await communicate.save(filepath)


@app.post("/voiceover", response_class=HTMLResponse)
async def voiceover(script_text: str = Form(...), voice: str = Form("en-US-GuyNeural")):
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", script_text[:30].lower())[:30] or "voiceover"
    filename = f"{safe_name}-{int(time.time())}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        await generate_voiceover(script_text, voice, filepath)
    except Exception as e:
        body_html = f"""
          <p style="color:#c0392b;">Voiceover generation failed: {esc(str(e))}</p>
          <h3>Script</h3>
          <textarea rows="22" style="width:100%;font-size:15px;">{esc(script_text)}</textarea>
          <p><a href="/">&larr; Start over</a></p>
        """
        return page(body_html)

    body_html = f"""
      <h3>Script</h3>
      <textarea rows="22" style="width:100%;font-size:15px;">{esc(script_text)}</textarea>
      <h3>Voiceover</h3>
      <audio controls src="/audio/{filename}" style="width:100%;"></audio><br>
      <a href="/audio/{filename}" download>Download voiceover (.mp3)</a>
      <p><a href="/">&larr; Start over</a></p>
    """
    return page(body_html)
