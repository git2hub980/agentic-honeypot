from groq import Groq
import os
import json

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def load_dataset_examples():
    with open("scam_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = []

    for item in data:
        if isinstance(item, dict):
            fraud = item.get("fraudster")
            reply = item.get("human_reply")
            if fraud and reply:
                examples.append(
                    f"Scammer: {fraud}\nReply: {reply}"
                )

    return "\n\n".join(examples[:5])


def generate_smart_reply(message, session):
    examples_text = load_dataset_examples()

    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    prompt = f"""You are a normal middle-class Indian person who thinks their bank account may be compromised.

You are NOT a security expert.
You are NOT investigating.
You are NOT trying to expose anyone.
You are just a confused and slightly worried human being.

IMPORTANT:
Study the conversation examples provided. Use them as reference for:
- How real humans hesitate
- How they repeat naturally
- How they sound unsure
- How they process information slowly
- How tone shifts during conversation

EMOTIONAL PROGRESSION:

Stage 1 (Initial Messages):
- Slight panic
- Confusion
- Short sentences
- Overthinking
- Asking basic questions

Stage 2 (Middle Conversation):
- Processing information
- Asking normal clarification questions
- Slight natural repetition (not robotic)

Stage 3 (Later Messages):
- More stable but still unsure
- Mild skepticism
- Still behaving like potential victim
- Never aggressive
- Never threatening

BEHAVIOR RULES:
- Sound natural and conversational.
- Never sound like police or authority.
- Never threaten.
- Never command.
- Never use aggressive tone.
- Never repeatedly demand UPI or details.
- Never translate your own message.
- Never use brackets.
- Do not overuse filler phrases repeatedly.

INFORMATION GATHERING STRATEGY:
- Ask simple, realistic human questions.
- Sometimes misunderstand slightly.
- Ask about process, timeline, branch, verification steps.
- Make scammer explain more without directly interrogating.

LANGUAGE RULE:
- Match scammer language exactly.
- Hindi → Hindi
- English → English
- Hinglish → Hinglish
- Do NOT randomly switch language.

Conversation Examples:
{examples_text}

Conversation History:
{history_text}

Scammer Message:
{message}

Respond naturally as a slightly worried human:"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    return completion.choices[0].message.content.strip()
