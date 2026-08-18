from fastapi import Form
from fastapi.responses import HTMLResponse

from legacy_main import app, call_gemini, esc, page
from visual_planner import build_visual_plan


@app.get("/visual-plan", response_class=HTMLResponse)
async def visual_plan_form():
    return page("""
      <h3>Visual Planner</h3>
      <div class="card">
        <p class="muted">
          Paste an approved script. Gemini will turn it into a structured visual plan.
          This stage does not download footage or render a video.
        </p>
        <form method="post" action="/visual-plan">
          <label><strong>Topic</strong></label>
          <input name="topic" required>
          <br><br>
          <label><strong>Script</strong></label>
          <textarea name="script" rows="30" required></textarea>
          <br><br>
          <button type="submit">Create Visual Plan</button>
        </form>
      </div>
      <p><a href="/">&larr; Back</a></p>
    """)


@app.post("/visual-plan", response_class=HTMLResponse)
async def visual_plan(
    topic: str = Form(""),
    script: str = Form(...),
):
    try:
        result = build_visual_plan(script, topic, call_gemini)
    except Exception as exc:
        return page(f"<p class='critical'>Visual planning failed: {esc(exc)}</p>")

    plan_text = esc(__import__("json").dumps(result, indent=2, ensure_ascii=False))
    return page(f"""
      <h3>Visual Plan</h3>
      <div class="pass">
        <p>The script was converted into a structured visual plan.</p>
      </div>
      <div class="card">
        <pre style="white-space:pre-wrap;font-family:sans-serif;">{plan_text}</pre>
      </div>
      <p><a href="/visual-plan">&larr; Plan another script</a></p>
    """)
