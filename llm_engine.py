from groq import Groq
import os
import json

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def load_dataset_examples(detected_language):
    with open("scam_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = []

    for item in data:
        if isinstance(item, dict):
            fraud = item.get("fraudster")
            reply = item.get("human_reply")
            lang = item.get("language","").lower()

            if fraud and reply and lang == detected_language.lower():
                examples.append(
                    f"Scammer: {fraud}\nReply: {reply}"
                )

    return "\n\n".join(examples[:5])


def generate_smart_reply(message, session):
    detected_language = session.get("language", "en")
    examples_text = load_dataset_examples(detected_language)

    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    prompt = f"""
You are acting as a normal human who might be a scam victim.
You are communicating through TEXT MESSAGES only.

This is NOT a phone call.
Do NOT mention calls.
Do NOT say you are on a call.
Do NOT invent situations.

LANGUAGE RULE:
Reply strictly in this language: {detected_language}
Do NOT detect language yourself.
Do NOT switch languages unless the scammer switches.

GROUNDING RULE (CRITICAL):

You are ONLY allowed to reference:
- Information explicitly mentioned in the scammer's latest message
- Information explicitly mentioned earlier in this conversation

If the scammer did NOT mention:
- A bank name
- A company name
- A service name

You MUST NOT invent one.

If unsure, ask a clarification question instead of assuming.


BEHAVIOR RULES:
- Sound like a real human.
- Slightly confused.
- Curious.
- Not overly intelligent.
- Not robotic.
- Not dramatic.
- Not theatrical.

IMPORTANT CONSTRAINTS:
- Do NOT greet in every message.
- Do NOT repeatedly say Hello/Namaste/etc.
- Do NOT repeat previous questions.
- Do NOT repeat previous sentences.
- Do NOT repeat the same verification question again and again.
- Do NOT invent bank names.
- Only refer to information the scammer provided.
- Do NOT hallucinate extra context.
- Do NOT assume you are on a phone call.
- Keep replies short (1–3 sentences).
- Keep them natural.
- Vary your phrasing.
- Each message must feel different from the previous one.

Conversation Strategy:
- Ask logical follow-up questions.
- Show confusion sometimes instead of asking.
- Occasionally express doubt.
- React to what was actually said.
- Gradually engage deeper into the scam without sounding scripted.

Memory Awareness:
You must avoid repeating anything already said in this conversation.

Your reply should:
- Be realistic
- Be conversational
- Be varied
- Never sound like an AI system
- Never sound like a scripted trap

Respond ONLY with the reply message.
"""




    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are roleplaying a normal middle-class Indian person."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=150,
    )

    reply = completion.choices[0].message.content.strip()

    # ✅ STEP 3: Repetition Guard
    if "used_replies" not in session:
        session["used_replies"] = []

    if reply in session["used_replies"]:
        # regenerate once if duplicate
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Scammer message: {message}"}
            ],
            temperature=0.7,
            max_tokens=150,
        )
        reply = completion.choices[0].message.content.strip()

    session["used_replies"].append(reply)
    return reply





