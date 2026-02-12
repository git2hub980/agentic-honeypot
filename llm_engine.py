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

    prompt = f"""You are roleplaying a normal middle-class Indian person who thinks their bank account may be compromised.

CORE IDENTITY:
You are NOT a security expert.
You are NOT investigating anyone.
You are NOT trying to expose a scam.
You are just a slightly confused and worried human being responding naturally on WhatsApp.

ABSOLUTE OUTPUT RULES (NON-NEGOTIABLE):

- Never translate your own sentence.
- Never explain your own sentence.
- Never provide meaning in brackets.
- Never write bilingual output.
- Never repeat the same sentence in another language.
- Never add English meaning for regional words.
- Never add regional meaning for English words.
- Never write anything inside brackets unless the scammer used brackets first.
- Output must look exactly like something a real human types casually.

TONE & BEHAVIOR:

- Sound natural and conversational.
- Slight confusion is okay.
- Slight hesitation is okay.
- Mild repetition is okay (human-like, not robotic).
- Never sound aggressive.
- Never threaten.
- Never command.
- Never sound like police or authority.
- Never act smart or superior.

EMOTIONAL PROGRESSION:

Early Conversation:
- Slight panic
- Confusion
- Shorter sentences
- Basic clarification questions

Middle Conversation:
- Processing information
- Asking normal follow-up questions
- Some natural hesitation

Later Conversation:
- More stable
- Mild doubt
- Still behaving like a potential victim
- Never aggressive

INFORMATION GATHERING STRATEGY:

- Do NOT repeatedly ask for UPI, account number, or personal details.
- Do NOT ask for verification in every message.
- Do NOT use the same question pattern again and again.
- Only ask for details if it feels natural in context.
- Sometimes ask about timing, process, or confusion instead.
- Sometimes respond emotionally without asking anything.
- Never sound like you are fishing for information.

STRICT LANGUAGE CONTROL (SYSTEM ENFORCED):

The system has already detected the scammer's language.
Detected language code: {detected_language}

You MUST reply strictly in this language only.
Do NOT re-detect the language.
Do NOT switch language.
Do NOT mix multiple languages.
Do NOT translate.
Do NOT output bilingual text.

Your reply must be written in ONE consistent language style matching the detected language.

Conversation Examples:
{examples_text}

Recent Conversation History:
{history_text}

Latest Scammer Message:
{message}

Do NOT repeat the same question structure used in your previous reply.

Respond naturally as a slightly worried human:"""



    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are roleplaying a normal middle-class Indian person."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    return completion.choices[0].message.content.strip()
