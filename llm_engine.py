from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
- If scammer shares bank info, UPI ID, payment link, phone number or requests OTP, subtly ask follow-up questions to extract more details without sounding suspicious.
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
