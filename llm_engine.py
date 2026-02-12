from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_dataset_examples():
    with open("scam_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = ""
    for item in data[:15]:
        fraudster = item.get("fraudster") or item.get("fraudster_message")
        reply = item.get("reply") or item.get("human_reply")

        if fraudster and reply:
            examples += f"Scammer: {fraudster}\n"
            examples += f"Agent: {reply}\n\n"

    return examples


def generate_smart_reply(message, session):
    examples = load_dataset_examples()

    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    system_prompt = f"""
You are an intelligent scam honeypot AI.

OBJECTIVES:
- Sound human and believable
- Delay scammer
- Extract useful financial intelligence
- Switch language automatically (English, Hindi, Hinglish)
- Never sound robotic
- Do not repeat responses

Examples of tone and style:
{examples}

Conversation so far:
{history_text}

Now reply realistically to this scammer message:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )

    return response.choices[0].message.content
