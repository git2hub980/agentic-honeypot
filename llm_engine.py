from groq import Groq
import os
import json
from language_detector import detect_language

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


# --------------------------------------------------
# Load dataset examples for grounding
# --------------------------------------------------
def load_dataset_examples(detected_language):
    try:
        with open("scam_dataset.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return ""

    examples = []

    for item in data:
        if isinstance(item, dict):
            fraud = item.get("fraudster")
            reply = item.get("human_reply")
            lang = item.get("language", "").lower()

            if fraud and reply and lang == detected_language.lower():
                examples.append(
                    f"Scammer: {fraud}\nReply: {reply}"
                )

    return "\n\n".join(examples[:5])


# --------------------------------------------------
# Main Reply Generator
# --------------------------------------------------
def generate_smart_reply(message, session):

    # 🔎 STEP 1: Detect language per message
    lang_data = detect_language(message)
    detected_language = lang_data["primary"]
    confidence = lang_data["confidence"]

    # Fallback if weak confidence
    if confidence < 0.4:
        detected_language = session.get("language", "en")

    session["language"] = detected_language

    # 📚 Load dataset examples
    examples_text = load_dataset_examples(detected_language)

    # 🧠 Conversation memory (last 5 scammer messages)
    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    # Mixed language note
    mixed_note = ""
    if lang_data.get("secondary"):
        mixed_note = "The scammer appears to be using mixed language. Respond naturally in a similar mixed style if needed."

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------
    prompt = f"""
You are acting as a normal middle-class Indian person texting on WhatsApp.

You are communicating through TEXT MESSAGES only.
This is NOT a phone call.
Do NOT mention calls.
Do NOT invent situations.

LANGUAGE RULE:
Reply strictly in this language: {detected_language}
Do NOT auto-detect language yourself.
Do NOT switch languages unless the scammer switches.
{mixed_note}

EXAMPLE CONVERSATIONS (reference tone & realism):
{examples_text}

Previous conversation context:
{history_text}

GROUNDING RULE (CRITICAL):
You are ONLY allowed to reference:
- Information explicitly mentioned in the scammer's latest message
- Information explicitly mentioned earlier in this conversation

If the scammer did NOT mention:
- A bank name
- A company name
- A service name

You MUST NOT invent one.
If unsure, ask for clarification instead of assuming.

BEHAVIOR RULES:
- Sound like a real human.
- Slightly confused.
- Curious.
- Not overly intelligent.
- Not robotic.
- Not dramatic.

TEXTING STYLE RULES:
- Use small letters only.
- Avoid full stops unless necessary.
- Use casual short forms sometimes:
    you → u
    okay → ok / k
    i guess → ig
    yes → yus
    no → nah
- Not perfect grammar.
- Sound like real whatsapp texting.

IMPORTANT CONSTRAINTS:
- Do NOT greet in every message.
- Do NOT repeat previous sentences.
- Do NOT REPEAT verification questions again and again.
- Do NOT hallucinate extra context.
- Keep replies short (1–3 sentences).
- Each message must feel different.

Respond ONLY with the reply message.

Scammer message: {message}
"""

    # --------------------------------------------------
    # Generate Reply
    # --------------------------------------------------
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are roleplaying a normal middle-class Indian person."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=150,
    )

    reply = completion.choices[0].message.content.strip()

    # --------------------------------------------------
    # Repetition Guard
    # --------------------------------------------------
    if "used_replies" not in session:
        session["used_replies"] = []

    if reply in session["used_replies"]:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are roleplaying a normal middle-class Indian person."
                },
                {
                    "role": "user",
                    "content": prompt + "\nMake the response different from previous ones."
                }
            ],
            temperature=0.8,
            max_tokens=150,
        )
        reply = completion.choices[0].message.content.strip()

    session["used_replies"].append(reply)

    return reply
