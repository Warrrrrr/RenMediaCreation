import os
import re
import time
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

SCRIPT_PROMPT_TEMPLATE = """You are a professional YouTube scriptwriter. Write a short-form video voiceover script (about {length} seconds when read aloud) on this topic: "{topic}".

Structure the script as one continuous narrative, not a list of numbered tips. Use these storytelling techniques throughout:
- Open with a hook that creates a curiosity gap in the first 2 sentences.
- Use "But" and "Therefore" to connect ideas causally instead of "and then".
- Include at least one open loop early on that gets resolved near the end.
- Vary pacing: shorter sentences for tension, longer sentences when building context.
- End with a clear, satisfying payoff and a short call to action to follow/subscribe.

Output ONLY the voiceover narration text, with no headers, labels, timestamps, or stage directions -- just the words a narrator would read aloud.
"""

VOICES = [
    ("en-US-GuyNeural", "Guy (US male)"),
    ("en-US-JennyNeural", "Jenny (US female)"),
    ("en-GB-RyanNeural", "Ryan (UK male)"),
    ("en-GB-SoniaNeural", "Sonia (UK female)"),
    ("en-ZA-LukeNeural", "Luke (South African male)"),
    ("en-ZA-LeahNeural", "Leah (South African female)"),
]


def build_html(script_text="", audio_url="", error=""):
    error_html = f'<p style="color:#c0392b;">{error}</p>' if error else ""
    script_html = (
        f"<h3>Script</h3><textarea rows='14' style='width:100%;font-size:16px;'>{script_text}</textarea>"
        if script_text else ""
    )
    audio_html = (
        f"<h3>Voiceover</h3><audio controls src='{audio_url}' style='width:100%;'></audio><br>"
        f"<a href='{audio_url}' download>Download voiceover (.mp3)</a>"
        if audio_url else ""
    )
    voice_options = "".join(f'<option value="{v}">{label}</option>' for v, label in VOICES)
    return f"""
    <html>
    <head>
      <title>Script + Voiceover Generator</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="font-family:sans-serif; max-width:600px; margin:20px auto; padding:0 12px;">
      <h2>Script + Voiceover Generator</h2>
      <form method="post" action="/generate">
        <label>Topic</label><br>
        <input name="topic" style="width:100%;padding:8px;font-size:16px;" required><br><br>
        <label>Target length (seconds)</label><br>
        <input name="length" value="60" style="width:100%;padding:8px;font-size:16px;"><br><br>
        <label>Voice</label><br>
        <select name="voice" style="width:100%;padding:8px;font-size:16px;">
          {voice_options}
        </select><br><br>
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate</button>
      </form>
      {error_html}
      {script_html}
      {audio_html}
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
async def home():
    return build_html()


def generate_script(topic: str, length: str) -> str:
    prompt = SCRIPT_PROMPT_TEMPLATE.format(topic=topic, length=length)
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(GEMINI_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def generate_voiceover(script_text: str, voice: str, filepath: str):
    communicate = edge_tts.Communicate(script_text, voice)
    await communicate.save(filepath)


@app.post("/generate", response_class=HTMLResponse)
async def generate(topic: str = Form(...), length: str = Form("60"), voice: str = Form("en-US-GuyNeural")):
    if not GEMINI_API_KEY:
        return build_html(error="Missing GEMINI_API_KEY -- add it in Render's Environment Variables, then redeploy.")

    try:
        script_text = generate_script(topic, length)
    except Exception as e:
        return build_html(error=f"Script generation failed: {e}")

    safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower())[:40] or "voiceover"
    filename = f"{safe_name}-{int(time.time())}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        await generate_voiceover(script_text, voice, filepath)
    except Exception as e:
        return build_html(script_text=script_text, error=f"Voiceover generation failed: {e}")

    return build_html(script_text=script_text, audio_url=f"/audio/{filename}")
