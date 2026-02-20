import random
import time


# -------------------------
# Natural filler replies
# -------------------------
FILLER_REPLIES = {
    "en": [
        "Ok I am checking",
        "Can you wait a minute?",
        "Let me verify once",
        "Something looks off here",
        "It is loading slowly",
        "There seems to be a delay",
        "It is asking for verification again",
        "System is showing an error",
        "Network seems unstable"
    ]
}


# -------------------------
# Targeted Intelligence Questions
# -------------------------
INTELLIGENCE_QUESTIONS = {
    "bank_fraud": [
        "Which branch is handling this?",
        "Can you confirm the account number again?",
        "Is this linked to my registered mobile number?",
        "What is the IFSC code there?",
    ],
    "upi_fraud": [
        "Which UPI ID should I verify?",
        "Is this linked to my Paytm or Google Pay?",
        "Can you resend the UPI ID?",
        "What number is registered for this cashback?",
    ],
    "phishing": [
        "Is this the official website?",
        "Can you resend the link?",
        "Why is the domain name different?",
        "Is this the secure page?",
    ],
    "generic": [
        "Can you explain that again?",
        "Which department are you from?",
        "Is this urgent?",
    ]
}


# -------------------------
# Red Flag Keywords
# -------------------------
RED_FLAGS = [
    "otp",
    "account number",
    "verify",
    "click",
    "urgent",
    "limited time",
    "transfer",
    "processing fee"
]


def detect_scam_type(session):
    signals = session.get("intelligence", {}).get("scamCategorySignals", [])

    if "bank_fraud" in signals:
        return "bank_fraud"
    if "reward_scam" in signals:
        return "upi_fraud"
    if "phishing" in signals:
        return "phishing"

    return "generic"


def detect_red_flags(message):
    message = message.lower()
    found = []

    for flag in RED_FLAGS:
        if flag in message:
            found.append(flag)

    return found


def agent_reply(session):

    intelligence = session.get("intelligence", {})
    confidence = session.get("confidence", 0)

    # -------------------------
    # Red flag tracking
    # -------------------------
    red_flags = detect_red_flags(message)
    session.setdefault("redFlagsDetected", [])
    session["redFlagsDetected"].extend(red_flags)
    session["redFlagsDetected"] = list(set(session["redFlagsDetected"]))

    # -------------------------
    # Choose scam type
    # -------------------------
    scam_type = detect_scam_type(session)

    # -------------------------
    # Early Stage (Build Trust)
    # -------------------------
    if confidence < 0.4:
        reply = random.choice(FILLER_REPLIES["en"])

    # -------------------------
    # Mid Stage (Extract Info)
    # -------------------------
    elif 0.4 <= confidence < 0.85:
        questions = INTELLIGENCE_QUESTIONS.get(scam_type, INTELLIGENCE_QUESTIONS["generic"])
        reply = random.choice(questions)

    # -------------------------
    # High Stage (Pressure Extraction)
    # -------------------------
    else:
        high_pressure_questions = [
            "Why is this so urgent?",
            "Can you confirm your official ID?",
            "Is this recorded for security?",
            "Can you provide your supervisor contact?"
        ]
        reply = random.choice(high_pressure_questions)

    time.sleep(random.uniform(0.6, 1.5))
    return reply
