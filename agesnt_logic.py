import random
import time
from scam_detector import detect_red_flags


# -------------------------
# Natural filler replies (early trust building)
# -------------------------
FILLER_REPLIES = [
    "Ok I am checking.",
    "Can you wait a minute?",
    "Let me verify once.",
    "Something looks off here.",
    "It is loading slowly.",
    "There seems to be a delay.",
    "It is asking for verification again.",
    "System is showing an error.",
    "Network seems unstable."
]


# -------------------------
# Targeted Intelligence Questions
# -------------------------
INTELLIGENCE_QUESTIONS = {
    "bank_fraud": [
        "Which branch is handling this?",
        "Can you confirm the account number again?",
        "Is this linked to my registered mobile number?",
        "What is the IFSC code there?"
    ],
    "upi_fraud": [
        "Which UPI ID should I verify?",
        "Is this linked to Paytm or Google Pay?",
        "Can you resend the UPI ID?",
        "What number is registered for this cashback?"
    ],
    "phishing": [
        "Is this the official website?",
        "Can you resend the link?",
        "Why is the domain name different?",
        "Is this the secure page?"
    ],
    "generic": [
        "Can you explain that again?",
        "Which department are you from?",
        "Is this urgent?"
    ]
}


# -------------------------
# Detect Scam Type from Extracted Intelligence
# -------------------------
def detect_scam_type(session):

    intel = session.get("intelligence", {})

    if intel.get("bankAccounts"):
        return "bank_fraud"

    if intel.get("upiIds"):
        return "upi_fraud"

    if intel.get("links"):
        return "phishing"

    return "generic"

def choose_next_intelligence_goal(session):
    extracted_info = session.get("intelligence",{})
    
    """
    Decide what intelligence we still need from the scammer.
    Returns a goal string that helps drive the next question.
    """

    if not extracted_info.get("payment_method"):
        return "ask_payment_method"

    if not extracted_info.get("account_number"):
        return "ask_account_number"

    if not extracted_info.get("amount"):
        return "ask_amount"

    if not extracted_info.get("bank_name"):
        return "ask_bank_name"

    return "stall"


# -------------------------
# Main Reply Generator
# -------------------------
def agent_reply(session, message):
    red_flags = detect_red_flags(message)

    confidence = session.get("confidence", 0)
    scam_type = detect_scam_type(session)

    # Track used replies to avoid repetition
    session.setdefault("used_replies", [])
    used = session["used_replies"]

    # -------------------------
    # Early Stage (Trust Building)
    # -------------------------
    if confidence < 0.4:
        options = FILLER_REPLIES

    # -------------------------
    # Mid Stage (Information Extraction)
    # -------------------------
    elif 0.4 <= confidence < 0.85:
        options = INTELLIGENCE_QUESTIONS.get(
            scam_type,
            INTELLIGENCE_QUESTIONS["generic"]
        )

    # -------------------------
    # High Stage (Pressure & Authority)
    # -------------------------
    else:
        options = [
            "Why is this so urgent?",
            "Can you confirm your official ID?",
            "Is this being recorded for security purposes?",
            "Can you provide your supervisor contact?"
        ]

    # Avoid repeating same reply
    reply = random.choice(options)
    attempts = 0
    while reply in used and attempts < 5:
        reply = random.choice(options)
        attempts += 1

    used.append(reply)
    session["used_replies"] = used[-10:]  # keep last 10 only

    # Simulate human delay
    time.sleep(random.uniform(0.6, 1.5))

    return reply
