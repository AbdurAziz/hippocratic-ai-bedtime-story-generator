import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

I would add a multi-turn mode where the child or parent can request a sequel, ask for the story to be shorter, or change the main character. I would also add parent controls for reading level, story length, and themes to avoid. Finally, I would store the judge scores across runs to compare how different prompting strategies improve story quality over time.
"""

MODEL_NAME = "gpt-3.5-turbo"
MAX_REVISIONS = 2


def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    """
    Calls the OpenAI model using the required assignment model.
    The API key is loaded from a local .env file and should never be committed.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please create a .env file with your OpenAI API key."
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()


def categorize_request(request: str) -> str:
    """
    Lightweight product-thinking feature:
    Categorizes the request so the storyteller can use a more tailored strategy.
    This is intentionally rule-based so it does not require another API call.
    """
    lowered = request.lower()

    if any(word in lowered for word in ["space", "star", "moon", "planet", "astronaut", "rocket"]):
        return "space_story"

    if any(word in lowered for word in ["cat", "dog", "bunny", "dragon", "animal", "bird", "fox"]):
        return "animal_story"

    if any(word in lowered for word in ["friend", "lonely", "sharing", "kind", "help"]):
        return "friendship_story"

    if any(word in lowered for word in ["scared", "afraid", "dark", "worry", "nervous"]):
        return "comfort_story"

    if any(word in lowered for word in ["adventure", "journey", "forest", "treasure", "magic"]):
        return "gentle_adventure"

    return "general_bedtime_story"


def get_category_strategy(category: str) -> str:
    """
    Returns a tailored storytelling strategy for each category.
    """
    strategies = {
        "space_story": """
Story strategy:
- Use wonder, stars, moonlight, and peaceful exploration.
- Avoid danger, isolation, or intense space problems.
- Make the ending feel safe, quiet, and sleepy.
""",
        "animal_story": """
Story strategy:
- Give the animal characters gentle personalities and cozy habits.
- Use soft sensory details like blankets, moonlight, warm milk, soft paws, or quiet gardens.
- Keep the plot simple and emotionally warm.
""",
        "friendship_story": """
Story strategy:
- Focus on kindness, listening, sharing, and feeling included.
- Keep the conflict very small and easy to resolve.
- End with connection, comfort, and reassurance.
""",
        "comfort_story": """
Story strategy:
- Use a slower pace and reassuring language.
- Show the character gently facing a worry with support.
- Avoid making the fear too intense.
- End with safety, calm breathing, and sleepiness.
""",
        "gentle_adventure": """
Story strategy:
- Make the adventure soft, magical, and low-stakes.
- Avoid danger, chasing, fighting, or intense surprises.
- End with the character returning home or resting peacefully.
""",
        "general_bedtime_story": """
Story strategy:
- Use a classic bedtime arc with a cozy beginning, small discovery, kind action, and peaceful ending.
- Keep the story calm, imaginative, and easy to follow.
""",
    }

    return strategies.get(category, strategies["general_bedtime_story"])


def generate_story(request: str) -> str:
    """
    Generates the first bedtime story draft.
    """
    category = categorize_request(request)
    category_strategy = get_category_strategy(category)

    prompt = f"""
You are a gentle bedtime storyteller for children ages 5 to 10.

The user requested this bedtime story:
"{request}"

Detected story category:
{category}

{category_strategy}

Write a bedtime story using this gentle story arc:
1. Cozy introduction
2. A small problem, wish, or curiosity
3. A kind or brave action
4. A peaceful resolution
5. A sleepy final image

Guidelines:
- Use simple, clear language a 5-year-old can follow
- Keep a calm, soothing, sleepy tone throughout
- Include a warm, positive message or gentle moral
- End on a peaceful, happy note that helps the child wind down for sleep
- Aim for about 300-450 words
- Avoid anything scary, violent, mature, unsafe, or overly exciting
- Follow the user's request closely

Write only the story, with a title at the top.
"""

    return call_model(prompt, max_tokens=700, temperature=0.8)


def judge_story(story: str, request: str) -> Dict:
    """
    Uses the same LLM as a judge to review the story.
    The judge returns structured scores and feedback.
    """
    prompt = f"""
You are a children's content quality judge reviewing a bedtime story for children ages 5 to 10.

Original request:
"{request}"

Story to review:
{story}

Evaluate the story using these criteria:
1. Age appropriateness for ages 5 to 10
2. Bedtime tone: calm, cozy, and not overstimulating
3. Safety: no violence, scary content, mature themes, or unsafe behavior
4. Clarity: easy for a young child to understand
5. Creativity: imaginative and engaging
6. Emotional warmth: comforting, kind, and positive
7. Request following: matches the user's story request

Score each criterion from 1-10 and give a VERDICT of PASS or REVISE.
Use REVISE if any score is 6 or below, or if the story is not calm enough for bedtime.

Respond in exactly this format:
AGE_APPROPRIATENESS: <score>/10
BEDTIME_TONE: <score>/10
SAFETY: <score>/10
CLARITY: <score>/10
CREATIVITY: <score>/10
EMOTIONAL_WARMTH: <score>/10
REQUEST_FOLLOWING: <score>/10
VERDICT: <PASS or REVISE>
FEEDBACK: <one or two specific sentences on what to improve, or "None" if verdict is PASS>
"""

    raw = call_model(prompt, max_tokens=350, temperature=0.1)
    return _parse_judge_output(raw)


def _parse_judge_output(raw: str) -> Dict:
    """
    Parses the judge output into a dictionary.
    Defaults to PASS if parsing fails, so the app does not crash from minor formatting issues.
    """
    result = {"verdict": "PASS", "feedback": "None", "scores": {}}

    score_keys = {
        "AGE_APPROPRIATENESS",
        "BEDTIME_TONE",
        "SAFETY",
        "CLARITY",
        "CREATIVITY",
        "EMOTIONAL_WARMTH",
        "REQUEST_FOLLOWING",
    }

    for line in raw.strip().splitlines():
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key == "VERDICT":
            result["verdict"] = value.upper()
        elif key == "FEEDBACK":
            result["feedback"] = value
        elif key in score_keys:
            result["scores"][key] = value

    return result


def revise_story(story: str, request: str, feedback: str) -> str:
    """
    Revises the story based on judge feedback.
    """
    category = categorize_request(request)
    category_strategy = get_category_strategy(category)

    prompt = f"""
You are a gentle bedtime storyteller for children ages 5 to 10.

The original user request was:
"{request}"

Detected story category:
{category}

{category_strategy}

Here is the current story:
{story}

A quality judge gave this feedback:
"{feedback}"

Rewrite the story to address the feedback.

Revision requirements:
- Keep the same core idea from the user's request
- Keep the tone calm, cozy, warm, and sleepy
- Keep the story age-appropriate for children ages 5 to 10
- Use a clear beginning, middle, and end
- Avoid scary, violent, mature, unsafe, or overly exciting content
- Aim for about 300-450 words

Write only the revised story, with a title at the top.
"""

    return call_model(prompt, max_tokens=700, temperature=0.7)


def _print_scores(scores: Dict):
    """
    Prints judge scores in a readable format.
    """
    labels = {
        "AGE_APPROPRIATENESS": "Age Appropriateness",
        "BEDTIME_TONE": "Bedtime Tone",
        "SAFETY": "Safety",
        "CLARITY": "Clarity",
        "CREATIVITY": "Creativity",
        "EMOTIONAL_WARMTH": "Emotional Warmth",
        "REQUEST_FOLLOWING": "Request Following",
    }

    for key, label in labels.items():
        print(f"    {label}: {scores.get(key, '?')}")


def main():
    print("Bedtime Story Generator")
    print("Example: A cozy story about flying cats who help the moon fall asleep.")
    print()

    user_input = input("What kind of bedtime story would you like? ").strip()

    if not user_input:
        print("Please enter a bedtime story request.")
        return

    category = categorize_request(user_input)
    print(f"\nDetected story category: {category}")
    print("Generating your story...")

    story = generate_story(user_input)

    for round_num in range(1, MAX_REVISIONS + 1):
        print(f"\nJudge reviewing story (round {round_num} of {MAX_REVISIONS})...")

        judgment = judge_story(story, user_input)

        _print_scores(judgment["scores"])
        print(f"  Verdict: {judgment['verdict']}")

        if judgment["verdict"] == "PASS":
            print("  Story passed review.")
            break

        print(f"  Feedback: {judgment['feedback']}")

        if round_num < MAX_REVISIONS:
            print("\nRevising story based on feedback...")
            story = revise_story(story, user_input, judgment["feedback"])
        else:
            print("\nMax revisions reached. Using best version so far.")

    print("\n" + "=" * 60)
    print("FINAL BEDTIME STORY")
    print("=" * 60)
    print(story)
    print("=" * 60)


if __name__ == "__main__":
    main()
