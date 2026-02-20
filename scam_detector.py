import re

# ----------------------------
# Keyword Weights
# ----------------------------

KEYWORDS = {
    "otp": 0.3,
    "verify": 0.2,
    "urgent": 0.25,
    "blocked": 0.25,
    "suspended": 0.25,
    "bank": 0.15,
    "account": 0.1,
    "click": 0.2,
    "upi": 0.25,
    "winner": 0.3,
    "transfer": 0.2,
    "payment": 0.2,
    "processing fee": 0.3,
    "beneficiary": 0.25,
    "refund": 0.2,
    "security code": 0.3,
    "act now": 0.25,
    "limited time": 0.25,
    "offer expires": 0.3,
    "cashback": 0.25
}


# ----------------------------
# Pattern Rules
# ----------------------------

OTP_PATTERN = r"\b\d{4,8}\b"
LINK_PATTERN = r"http[s]?://"
PHONE_PATTERN = r"(?:\+91[-\s]?)?[6-9]\d{9}"


# ----------------------------
# Progressive Confidence
# ----------------------------

def progressive_confidence(message, history):

    score = 0.0
    text = message.lower()

    # 1️⃣ Keyword scoring
    for kw, weight in KEYWORDS.items():
        if kw in text:
            score += weight

    # 2️⃣ OTP number near keyword
    if "otp" in text and re.search(OTP_PATTERN, message):
        score += 0.3

    # 3️⃣ Suspicious link detection
    if re.search(LINK_PATTERN, text):
        score += 0.25

    # 4️⃣ Phone number request
    if re.search(PHONE_PATTERN, message):
        score += 0.15

    # 5️⃣ Urgency patterns
    if "2 hours" in text or "10 minutes" in text:
        score += 0.2

    # 6️⃣ Escalation factor
    scammer_turns = len([m for m in history if m["role"] == "scammer"])
    score += min(scammer_turns * 0.03, 0.25)

    return min(score, 1.0)


# ----------------------------
# Red Flag Detection (NEW)
# ----------------------------

def detect_red_flags(message):

    text = message.lower()
    red_flags = []

    if "urgent" in text or "act now" in text:
        red_flags.append("urgency_tactic")

    if "otp" in text:
        red_flags.append("otp_request")

    if "verify your account" in text:
        red_flags.append("account_verification_scam")

    if "cashback" in text or "winner" in text:
        red_flags.append("fake_reward")

    if re.search(LINK_PATTERN, text):
        red_flags.append("phishing_link")

    if "processing fee" in text:
        red_flags.append("advance_fee_scam")

    return list(set(red_flags))
