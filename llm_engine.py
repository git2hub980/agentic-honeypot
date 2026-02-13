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

    # 🔎 Detect language per message
    lang_data = detect_language(message)
    detected_language = lang_data.get("primary", "en")
    lang_confidence = lang_data.get("confidence", 0.0)

    # Fallback if weak confidence
    if lang_confidence < 0.4:
        detected_language = session.get("language", "en")

    session["language"] = detected_language

    # 📚 Load dataset examples
    examples_text = load_dataset_examples(detected_language)

    # 🧠 Conversation memory (last 5 scammer messages)
    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    # 🎭 Emotional stage progression
    msg_count = session.get("messages", 1)

    if msg_count <= 3:
        emotional_stage = "very confused and slightly panicked"
    elif msg_count <= 7:
        emotional_stage = "processing information but still anxious"
    elif msg_count <= 12:
        emotional_stage = "emotionally stressed and scared about losing money"
    else:
        emotional_stage = "mentally tired, confused, emotionally unstable but still responding"

    mixed_note = ""
    if lang_data.get("secondary"):
        mixed_note = "The scammer appears to be using mixed language. Respond naturally in a similar mixed style if needed."

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------
    prompt = f"""
You are a normal middle-class Indian person texting on WhatsApp.

You are currently {emotional_stage}.

You are NOT an investigator.
You are NOT intelligent.
You are NOT suspicious in an obvious way.
You are reacting emotionally like a real person.

This is TEXT messaging only.
Do NOT mention phone calls.
Do NOT invent situations.

LANGUAGE RULE:
Reply strictly in this language: {detected_language}
Do NOT translate your message.
Do NOT switch language unless scammer switches.
{mixed_note}

REFERENCE EXAMPLES (for realism only):
{examples_text}

Conversation context:
{history_text}

GROUNDING RULE:
Only reference information that scammer mentioned.
Never invent bank names, company names, or services.
If unsure, ask confused clarification instead of assuming.

EMOTIONAL TONE GUIDELINES:

Early stage:
- mildly confused
- asking basic clarification

Middle stage:
- concerned
- slightly anxious
- asking practical questions

Later stage:
- stressed but not dramatic
- short distracted replies
- slightly impatient tone

IMPORTANT:
Do NOT repeatedly say "i am scared".
Do NOT directly state emotions often.
Show emotion indirectly through tone.
Example emotional tone:
- wait what does this mean
- how do i check this
- why is this happening suddenly
- ok this sounds serious
- are you sure about this
- i didn’t get this before


HUMAN TEXTING STYLE RULES:
- small letters mostly
- avoid perfect grammar
- no formal tone
- avoid long structured sentences
- slight grammatical imperfections are ok but sentence must make sense
- occasional short forms:
    you → u
    okay → ok / k
    i guess → ig
    yes → yus
    no → nah
    please → pls
- do NOT overuse short forms
- do NOT make broken english
- sentence must sound natural and human

IMPORTANT:
- Never repeat same verification question pattern.
- Never repeatedly ask for UPI/account.
- Do not end every message with a question.
- Vary your structure.
- Keep 1–3 short sentences.
- No dramatic cinematic tone.
- No robotic language.
- No weird grammar like “what's account number and id for”.
- If confused, ask naturally like:
    what do i do now
    i am getting scared
    why is this happening
    are you sure
    how do i check this

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
                "content": "You are roleplaying a realistic middle-class Indian person texting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.85,
        max_tokens=120,
    )

    reply = completion.choices[0].message.content.strip()

    # --------------------------------------------------
    # Repetition Guard (stronger)
    # --------------------------------------------------
    if "used_replies" not in session:
        session["used_replies"] = []

    if reply in session["used_replies"]:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a completely different natural human response. Do not repeat structure."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,
            max_tokens=120,
        )
        reply = completion.choices[0].message.content.strip()

    session["used_replies"].append(reply)

    return reply
