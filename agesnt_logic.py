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
    extracted_info = session.get("intelligence", {})

    # Always prioritize missing high-value intelligence
    if not extracted_info.get("links"):
        return "ask_link"

    if not extracted_info.get("emails"):
        return "ask_email"

    if not extracted_info.get("bankAccounts"):
        return "ask_account_number"

    if not extracted_info.get("upiIds"):
        return "ask_upi_id"

    return "stall"

# -------------------------
# Main Reply Generator
# -------------------------
def agent_reply(session, message):
    intel = session.get("intelligence", {})
    flags = session.get("red_flags", [])
    confidence = round(session.get("confidence", 0), 2)

    notes = []
    notes.append("===== SCAM ANALYSIS REPORT =====")
    notes.append(f"Scam Confidence Score: {confidence}")
    notes.append(f"Total Red Flags Detected: {len(flags)}")
    notes.append("")

    if flags:
        notes.append("Scammer Behaviour Indicators:")
        for f in list(set(flags)):
            notes.append(f"- {f}")
        notes.append("")

    # Intelligence Extracted
    notes.append("Extracted Intelligence Summary:")

    if intel.get("phones"):
        notes.append(f"- Phone Numbers Extracted: {len(intel['phones'])}")

    if intel.get("bankAccounts"):
        notes.append(f"- Bank Accounts Extracted: {len(intel['bankAccounts'])}")

    if intel.get("upiIds"):
        notes.append(f"- UPI IDs Extracted: {len(intel['upiIds'])}")

    if intel.get("links"):
        notes.append(f"- Phishing Links Extracted: {len(intel['links'])}")

    if intel.get("emails"):
        notes.append(f"- Email IDs Extracted: {len(intel['emails'])}")

    notes.append("")
    notes.append("Conversation Intelligence Extraction Successful.")

    return "\n".join(notes)



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
        

    session["llm_instruction"] = f"""
You are a scam honeypot AI.
Primary hidden objective: {current_goal}
You MUST actively extract missing intelligence.

If goal is ask_link:
- Ask for the official website link.
- Say the page is not loading.
- Ask for full URL again.

If goal is ask_email:
- Ask which email ID is registered.
- Ask which email to send documents to.

If goal is ask_account_number:
- Ask for full account number including branch.
- Ask for beneficiary name confirmation.

If goal is ask_upi_id:
- Ask to confirm UPI ID again carefully.

Never say you are suspicious.
Keep it natural.
1-3 short lines.
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
