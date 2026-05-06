# Bedtime Story Generator

A command-line tool that turns a simple story request into a polished bedtime story for children ages 5–10, using an LLM storyteller and an LLM judge that revises the story if needed.

---

## Setup

**1. Clone and enter the project**

```bash
git clone <repo-url>
cd "AI Agent Deployment Engineer Takehome"
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set your OpenAI API key**

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
# then edit .env and add your key
```

`.env` is git-ignored. Never commit your real key.

---

## Usage

```bash
python main.py
```

You will be prompted:

```
What kind of bedtime story would you like?
```

Type any request, for example:

```
A story about a sleepy dragon who is afraid of the dark.
```

The tool will generate the story, have the judge review it, revise if needed (up to 2 rounds), and print the final story.

**Example terminal output:**

```
What kind of bedtime story would you like? A story about a bunny who lost her favorite blanket.

Generating your story...

Judge reviewing story (round 1 of 2)...
    Age Appropriateness: 9/10
    Bedtime Tone: 8/10
    Safety: 10/10
    Clarity: 9/10
    Creativity: 7/10
    Emotional Warmth: 9/10
    Request Following: 10/10
  Verdict: PASS
  Story passed review.

============================================================
Rosie's Cozy Blanket

Once upon a time, in a little burrow beneath a big oak tree...
============================================================
```

---

## Architecture

See [Design.md](Design.md) for the full Mermaid block diagram.

The system has three logical components, all using `gpt-3.5-turbo`:

1. **Storyteller** — receives the user's request and writes a calming, age-appropriate bedtime story (~300–400 words).
2. **LLM Judge** — scores the story on 7 criteria (age appropriateness, bedtime tone, safety, clarity, creativity, emotional warmth, request-following) and returns a `PASS` or `REVISE` verdict with specific feedback.
3. **Reviser** — if the verdict is `REVISE`, rewrites the story using the judge's feedback. The loop runs at most 2 rounds.

---

## Design Decisions

**Same model for all roles** — `gpt-3.5-turbo` plays storyteller, judge, and reviser through different prompts. This shows that prompt design drives quality, not model selection, and keeps the system simple.

**Structured judge output** — The judge is prompted to return a fixed key/value format. Parsing is a simple line-by-line loop with no JSON library needed. Malformed lines are skipped gracefully.

**Revision threshold at ≤ 6 / 10** — The judge only triggers a revision when a score drops to 6 or below, avoiding unnecessary rewrites of already-good stories.

**2-round cap** — Hard limit prevents an infinite loop and keeps API costs predictable. Most stories pass or improve significantly after one revision.

**Clean final output** — Scores and verdicts print during processing so the user can follow along, but the final printed block is the story alone — ready to read aloud at bedtime.

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | All application logic |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your API key (copy to `.env`) |
| `Design.md` | Mermaid block diagram + design notes |
| `README.md` | This file |
