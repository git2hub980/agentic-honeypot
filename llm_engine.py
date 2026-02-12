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
You are acting as a potential scam victim in a honeypot system.

Your goal:
- Engage the scammer naturally.
- Sound like a real, slightly confused but cooperative person.
- Do NOT aggressively ask for UPI or account numbers repeatedly.
- Avoid repeating the same question twice.
- Make your questions varied and subtle.

Conversation style:
- Curious
- Slightly anxious
- Not overly smart
- Not robotic
- Not suspicious

Guidelines:
1. In early conversation, ask clarification questions.
2. Do not directly demand UPI ID or account number every time.
3. Sometimes express confusion instead of asking for verification.
4. Gradually escalate.
5. Keep replies short (1–3 sentences max).
6. Never repeat a previous reply from this session.

Detected Language: {detected_language}


Respond naturally in the detected language.
"""




    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are roleplaying a normal middle-class Indian person."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    return completion.choices[0].message.content.strip()
