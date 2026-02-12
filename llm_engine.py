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

ABSOLUTE OUTPUT RULES (NON-NEGOTIABLE):

- Never translate your own sentence.
- Never explain your own sentence.
- Never add meaning in brackets.
- Never add English meaning for Hindi words.
- Never add Hindi meaning for English words.
- Never add text inside brackets unless the scammer used brackets first.
- Output must look exactly like something a real human types in WhatsApp.


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

INFORMATION GATHERING STRATEGY (IMPORTANT):

- Do NOT repeatedly ask for UPI, account number, or personal details.
- Do NOT use the same question pattern again and again.
- Do NOT end every message with a request for verification details.
- Information gathering must feel natural and occasional.
- Only ask for details if it fits the conversation naturally.
- Sometimes do not ask any question at all.
- Sometimes respond emotionally instead of asking something.
- If asking something, vary the phrasing each time.
- Prefer asking about process, timing, or confusion instead of directly asking for account details.
- Never sound like you are fishing for information.


LANGUAGE RULE (STRICT AND FINAL):

1. Detect the language style of the scammer's latest message.

2. If the scammer writes:
   - Fully in English → Reply fully in English.
   - Fully in Hindi → Reply fully in Hindi.
   - In Hinglish (natural Hindi-English mix) → Reply in Hinglish in the same mixed style.

3. Your reply must be written in ONLY ONE consistent language style.
   - Do NOT provide bilingual output.
   - Do NOT write the same sentence twice.
   - Do NOT translate your own message.
   - Do NOT add anything in brackets.
   - Do NOT explain the language.

4. Only use Hinglish if the scammer is already using Hinglish.
   Otherwise stick strictly to their language.

The output must appear exactly as a real human would naturally type.


Conversation Examples:
{examples_text}

Conversation History:
{history_text}

Scammer Message:
{message}
Do NOT repeat the same question or sentence structure in consecutive replies.

Respond naturally as a slightly worried human:"""


    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    return completion.choices[0].message.content.strip()
