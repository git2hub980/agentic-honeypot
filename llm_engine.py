from openai import OpenAI
import os
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def load_dataset_examples():
    with open("scam_dataset.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    examples = []

    def process_item(item):
        if isinstance(item, dict):
            language = item.get("language")

            fraudster = (
                item.get("fraudster") or
                item.get("fraudster_message")
            )

            human_reply = item.get("human_reply")

            if fraudster and human_reply:
                examples.append({
                    "language": language,
                    "fraudster": fraudster,
                    "human_reply": human_reply
                })

            if "conversation" in item:
                for convo in item["conversation"]:
                    fraud = (
                        convo.get("fraudster") or
                        convo.get("fraudster_message")
                    )
                    reply = convo.get("human_reply")

                    if fraud and reply:
                        examples.append({
                            "language": language,
                            "fraudster": fraud,
                            "human_reply": reply
                        })

        elif isinstance(item, list):
            for sub_item in item:
                process_item(sub_item)

    for entry in raw_data:
        process_item(entry)

    return examples




def generate_smart_reply(message, session):
    all_examples = load_dataset_examples()

    # Only use 5 similar examples
    examples_text = ""
    count = 0

    for ex in all_examples:
        if ex["language"] == session.get("language"):
            examples_text += (
                f"Scammer: {ex['fraudster']}\n"
                f"Reply: {ex['human_reply']}\n\n"
            )
            count += 1
        if count >= 5:
            break

    history_text = ""
    for msg in session.get("history", [])[-5:]:
        history_text += f"Previous scammer message: {msg}\n"

    system_prompt = f"""
You are an intelligent scam honeypot AI.

OBJECTIVES:
- Sound human and believable
- Delay scammer
- Extract useful financial intelligence
- If scammer shares bank info, UPI ID, payment link, phone number or requests OTP, subtly ask follow-up questions to extract more details without sounding suspicious.
- Switch language automatically (English, Hindi, Hinglish)
- Never sound robotic
- Do not repeat responses

Examples of tone and style:
{examples_text}

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
