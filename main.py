import os
import re
import time
import html
import requests
import edge_tts
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
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

OUTLINE_PROMPT_TEMPLATE = """You are a professional long-form YouTube scriptwriter and story architect. Plan the STRUCTURE for a video on this topic: "{topic}".

Target spoken length: approximately {length_minutes} minutes (about {word_target} words of narration).

Output a structured beat sheet, NOT prose narration. Use this exact format, one beat per line:

[SECTION NAME] -- Purpose/content of this beat (1-3 sentences describing what happens and which technique it uses)

Follow this architecture:
1. Cold Open / Hook (roughly first 5% of runtime) -- create a curiosity gap in the first two lines.
2. Macro Open Loop -- plant one compelling question or tease early that will only fully resolve near the end (the Zeigarnik effect: unresolved things stick in memory).
3. Four to six escalating Acts/Sections -- each section should:
   - Build on the previous one using "But" / "Therefore" causal logic, not "and then"
   - Contain its own small open loop or pattern interrupt (a tone shift, a rhetorical question, an unexpected turn) roughly every 60-90 seconds of runtime, to reset viewer attention
   - Use foot-in-the-door content logic: early sections introduce small, easy-to-agree-with ideas that later sections build into bigger, more surprising claims
4. One Audience Foot-in-the-Door Moment -- placed roughly two-thirds of the way through: a small, low-friction ask of the viewer (guess an answer, comment one word, etc.) that primes them to say "yes" to the bigger ask later.
5. Climax -- where the macro open loop from step 2 gets resolved.
6. Payoff / Resolution -- the satisfying takeaway.
7. Outro / CTA -- a natural subscribe ask that follows from the audience foot-in-the-door moment planted earlier.

Rules:
- Do not write any actual narration text yet -- structural plan only.
- Do not invent or reference specific named studies, researchers, or statistics -- describe psychological techniques generically (e.g. "plant an open loop here") without fabricating sources.
- Keep each beat description concise.
"""

SCRIPT_PROMPT_TEMPLATE = """You are a professional long-form YouTube scriptwriter. Expand the following APPROVED beat outline into a complete voiceover narration script for a video on: "{topic}".

Target spoken length: approximately {length_minutes} minutes (about {word_target} words).

APPROVED OUTLINE:
{outline}

Write the full narration following this outline's structure and beats, in order. Rules:
- Output ONLY the spoken narration text a narrator would read aloud -- no section headers, timestamps, labels, or stage directions.
- Write it as one continuous piece, not a list of separate segments.
- Use "But" and "therefore" (or natural equivalents) to connect ideas causally rather than "and then".
- Vary sentence pacing: short, punchy sentences during tense/pattern-interrupt beats; longer explanatory sentences when building context.
- Do not invent or cite specific named studies, researchers, or statistics -- use soft, generic attribution only for well-established ideas (e.g. "many psychologists point to...") and never fabricate a source.
- Follow the outline's placement of the open loop resolution, the audience foot-in-the-door moment, and the CTA exactly as planned.
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


@app.get("/", response_class=HTMLResponse)
async def home():
    body_html = """
      <form method="post" action="/outline">
        <label>Topic</label><br>
        <input name="topic" style="width:100%;padding:8px;font-size:16px;" required><br><br>
        <label>Target length (minutes)</label><br>
        <input name="length_minutes" value="10" style="width:100%;padding:8px;font-size:16px;"><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate Outline</button>
      </form>
    """
    return page(body_html)


@app.post("/outline", response_class=HTMLResponse)
async def outline(topic: str = Form(...), length_minutes: str = Form("10")):
    if not GEMINI_API_KEY:
        return page("<p style='color:#c0392b;'>Missing GEMINI_API_KEY -- add it in Render's Environment Variables, then redeploy.</p>")

    word_target = int(float(length_minutes) * WORDS_PER_MINUTE)
    prompt = OUTLINE_PROMPT_TEMPLATE.format(topic=topic, length_minutes=length_minutes, word_target=word_target)

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
    prompt = SCRIPT_PROMPT_TEMPLATE.format(topic=topic, length_minutes=length_minutes, word_target=word_target, outline=outline)

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
