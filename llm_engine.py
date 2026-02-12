from groq import Groq
import os
import json

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def load_dataset_examples():
    with open("scam_dataset.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    examples = []

    for item in raw_data:
        if isinstance(item, dict):
            fraud = item.get("fraudster")
            reply = item.get("human_reply")
            if fraud and reply:
                examples.append(
                    f"Scammer: {fraud}\nReply: {reply}\n"
                )

    return "\n".join(examples[:5])  # only 5 examples


def generate_smart_reply(message, session):
    examples_text = load_dataset_examples()

    prompt = f"""
You are a smart scam honeypot AI.

Be realistic.
Delay scammer.
Extract financial info subtly.
Switch language automatically.

Examples:
{examples_text}

Scammer message:
{message}

Reply:
"""

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return completion.choices[0].message.content
