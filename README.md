# Bedtime Story Generator

A command-line tool that turns a simple story request into a polished bedtime story for children ages 5–10, using an LLM storyteller, lightweight request categorization, an LLM judge, and a bounded revision loop.

The goal of this project is to create safe, cozy, age-appropriate bedtime stories while demonstrating prompt quality, clean Python code, and product thinking.

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

Your `.env` file should look like this:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

`.env` is git-ignored. Never commit your real API key.

---

## Usage

```bash
python main.py
```

You will be prompted:

```text
What kind of bedtime story would you like?
```

Type any request, for example:

```text
A story about a sleepy dragon who is afraid of the dark.
```

The tool will:

1. Categorize the request.
2. Select a tailored story strategy.
3. Generate an initial bedtime story.
4. Ask an LLM judge to review the story.
5. Revise the story if needed, up to 2 rounds.
6. Print the final polished bedtime story.

---

## Example Terminal Output

```text
What kind of bedtime story would you like? A story about a bunny who lost her favorite blanket.

Detected story category: animal_story
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
FINAL BEDTIME STORY
============================================================
Rosie's Cozy Blanket

Once upon a time, in a little burrow beneath a big oak tree...
============================================================
```

---

## Architecture

See [Design.md](Design.md) for the full Mermaid block diagram and system design notes.

The system has four logical components:

1. **Request Categorizer** — classifies the user's request into a story type such as `animal_story`, `space_story`, `comfort_story`, `friendship_story`, `gentle_adventure`, or `general_bedtime_story`.
2. **Storyteller** — receives the user's request, the detected category, and a tailored story strategy, then writes a calming, age-appropriate bedtime story.
3. **LLM Judge** — scores the story on age appropriateness, bedtime tone, safety, clarity, creativity, emotional warmth, and request-following. It returns a `PASS` or `REVISE` verdict with specific feedback.
4. **Reviser** — if the judge returns `REVISE`, rewrites the story using the judge's feedback. The loop runs at most 2 rounds.

All LLM calls use the assignment-provided model:

```text
gpt-3.5-turbo
```

The model name is stored in `MODEL_NAME` so it is easy to verify and preserve.

---

## Prompting Strategy

The project uses three main prompting stages.

### 1. Storyteller Prompt

The storyteller prompt asks the model to act as a gentle bedtime storyteller for children ages 5 to 10.

It includes constraints for:

- Age-appropriate language
- Calm bedtime tone
- Clear beginning, middle, and end
- Positive emotional message
- Safe content
- Request-following
- A target length of about 300 to 450 words

The prompt also uses a gentle story arc:

1. Cozy introduction
2. Small problem, wish, or curiosity
3. Kind or brave action
4. Peaceful resolution
5. Sleepy final image

### 2. Judge Prompt

The judge prompt asks the LLM to evaluate the story using a structured rubric.

The judge scores:

- Age appropriateness
- Bedtime tone
- Safety
- Clarity
- Creativity
- Emotional warmth
- Request following

The judge returns either `PASS` or `REVISE`.

### 3. Revision Prompt

If the judge returns `REVISE`, the revision prompt asks the model to improve the story based on the judge feedback while preserving the original user request, bedtime tone, age appropriateness, and safety constraints.

The revision loop is capped at 2 rounds to avoid unnecessary API calls and keep the system predictable.

---

## Request Categorization

To add product thinking without overcomplicating the project, the system includes a lightweight request categorizer.

The categorizer uses keyword rules to detect story types such as:

- `space_story`
- `animal_story`
- `friendship_story`
- `comfort_story`
- `gentle_adventure`
- `general_bedtime_story`

Each category maps to a tailored story strategy.

For example:

- Animal stories use gentle animal personalities, cozy settings, and soft sensory details.
- Space stories use wonder, stars, moonlight, and peaceful exploration.
- Comfort stories use slower pacing and reassuring language.
- Gentle adventures stay magical and low-stakes instead of intense or scary.

This improves story quality without requiring another LLM call, which keeps the system cheaper, faster, and easier to explain.

---

## Design Decisions

**Same model for all LLM roles**  
`gpt-3.5-turbo` plays storyteller, judge, and reviser through different prompts. This preserves the assignment-provided model while showing how prompt design can create different agent behaviors.

**Rule-based request categorization**  
The categorizer is intentionally lightweight and does not require an extra LLM call. It uses keywords to select a tailored storytelling strategy, improving output quality while keeping cost, latency, and complexity low.

**Tailored story strategies**  
Each category has a different generation strategy. This makes the output feel more intentional than a single generic bedtime story prompt.

**Structured judge output**  
The judge is prompted to return a fixed key/value format. Parsing is handled with a simple line-by-line loop, keeping the code readable and avoiding unnecessary complexity.

**Revision threshold at ≤ 6 / 10**  
The judge only triggers a revision when a score drops to 6 or below, or when the story is not calm enough for bedtime. This avoids unnecessary rewrites of already-good stories.

**2-round cap**  
A hard limit prevents infinite loops and keeps API costs predictable. Most stories should pass or improve significantly after one revision.

**Clean final output**  
Scores and verdicts print during processing so the quality-control loop is visible, but the final output clearly separates the polished bedtime story.

---

## Evaluation Alignment

### Prompt Quality

This project uses separate prompts for story generation, judging, and revision. The storyteller prompt includes age range, bedtime tone, safety constraints, story length, request-following, and a gentle story arc. The judge prompt uses a structured rubric to evaluate whether the story should pass or be revised.

### Code Quality

The code is organized into small, readable functions for:

- Calling the model
- Categorizing the request
- Selecting a story strategy
- Generating the story
- Judging the story
- Parsing judge output
- Revising the story
- Printing judge scores
- Running the command-line interface

The API key is loaded from environment variables and is never hardcoded. The model name is stored in a constant and kept as `gpt-3.5-turbo` to preserve the assignment requirement.

### Creativity & Product Thinking

The system goes beyond a single story prompt by adding request categorization, tailored story strategies, a structured judge rubric, and a bounded revision loop. This makes the tool feel more like a small product pipeline rather than a one-shot prompt.

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main application logic |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for the OpenAI API key. Copy to `.env` |
| `Design.md` | Mermaid block diagram and design notes |
| `README.md` | Setup, usage, architecture, and evaluation alignment |

---

## API Key Safety

The OpenAI API key is loaded from a local `.env` file using `python-dotenv`.

The `.gitignore` file should include:

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/
.DS_Store
```

This prevents the real API key and local environment files from being pushed to GitHub.

---

## What I Would Build Next

With two more hours, I would add:

1. A multi-turn mode where the child or parent can request a sequel, shorter version, or different main character.
2. Parent controls for reading level, story length, and themes to avoid.
3. A simple score history view to compare judge scores across revision rounds.
4. More story categories with tailored narrative arcs.
5. Optional saving of final stories to text files.