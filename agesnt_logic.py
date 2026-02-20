import random
import time
from scam_detector import detect_red_flags
from llm_engine import generate_smart_reply


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
    session.setdefault("goals_asked", [])
    
    """
    Decide what intelligence we still need from the scammer.
    Returns a goal string that helps drive the next question.
    """

    if not extracted_info.get("links") and "ask_link" not in session["goals_asked"]:
        session["goals_asked"].append("ask_link")
        return "ask_link"

    if not extracted_info.get("bankAccounts") and "ask_account_number" not in session["goals_asked"]:
        session["goals_asked"].append("ask_account_number")
        return "ask_account_number"

    if not extracted_info.get("upiIds") and "ask_upi_id" not in session["goals_asked"]:
        session["goals_asked"].append("ask_upi_id")
        return "ask_upi_id"

    if not extracted_info.get("phones") and "ask_phone_number" not in session["goals_asked"]:
        session["goals_asked"].append("ask_phone_number")
        return "ask_phone_number"

    if not extracted_info.get("emails") and "ask_email" not in session["goals_asked"]:
        session["goals_asked"].append("ask_email")
        return "ask_email"

    return "stall"


# -------------------------
# Main Reply Generator
# -------------------------
def agent_reply(session, message):
    red_flags = detect_red_flags(message)

    
    # Track used replies to avoid repetition
    session.setdefault("used_replies", [])
    session.setdefault("red_flags",[])
    session.setdefault("goals_asked", [])
    session.setdefault("stage", "initial")
    
    session["red_flags"].extend(red_flags)

    confidence = session.get("confidence", 0)
    scam_type = detect_scam_type(session)
    current_goal = choose_next_intelligence_goal(session)
    session["current_goal"] = current_goal



    # -------------------------
    # Early Stage (Trust Building)
    # -------------------------
    if confidence < 0.4:
        session["stage"] = "trust_building"
        stage_hint = "You are mildly confused and just starting to process this."
        options = FILLER_REPLIES

    # -------------------------
    # Mid Stage (Information Extraction)
    # -------------------------
    elif 0.4 <= confidence < 0.85:
        session["stage"] = "information_gathering"
        stage_hint = "You are concerned and trying to understand practical details."
        options = INTELLIGENCE_QUESTIONS.get(
            scam_type,
            INTELLIGENCE_QUESTIONS["generic"]
        )

    # -------------------------
    # High Stage (Pressure & Authority)
    # -------------------------
    else:
        session["stage"] = "extraction_pressure"
        stage_hint = "You are stressed and slightly suspicious but still emotional."
        options = [
             "Why is this so urgent?",
             "Can you confirm your official ID?",
             "Is this being recorded for security purposes?",
             "Can you provide your supervisor contact?",
             "Which department are you calling from?",
             "Is this monitored officially?",
             "Can you share your employee ID?",
             "Is there a ticket number for this case?",
             "Who authorized this transaction?",
             "Before I proceed, please confirm the exact account I need to transfer to.",
             "Can you send the official payment link again?",
             "Which UPI ID should I enter exactly?",
             "Please confirm the full account number including branch details.",
             "Is this the final beneficiary account?"
]
        ]

    session["llm_instruction"] = f"""
You are a scam honeypot AI.
Primary hidden objective: {current_goal}
Conversation stage: {session["stage"]}
Emotional state:
{stage_hint}

Strategic rules:
- Ask probing questions naturally.
- Never copy dataset examples directly.
- Avoid robotic phrasing.
- Keep responses 1-3 short natural lines.
- If link appears, ask what page it opens.
- If payment mentioned, confirm beneficiary details.
- If OTP appears, ask how it connects to account.
- Extract missing intelligence carefully.
"""
    reply = generate_smart_reply(message,session)
    # Avoid repeating anything from last 3 replies
    recent_replies = session["used_replies"][-3:]

    if reply in recent_replies:
        reply = generate_smart_reply(message, session)

    session["used_replies"].append(reply)
    session["used_replies"] = session["used_replies"][-10:]

    # -------------------------
    # Human Delay
    # -------------------------
    time.sleep(random.uniform(0.6, 1.5))

    return reply
