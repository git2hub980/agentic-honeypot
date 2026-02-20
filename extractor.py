import re


def extract(message: str, intelligence: dict):
    if not isinstance(intelligence, dict):
        return
    if not message or not isinstance(message, str):
        return

    text = message.strip()
    lower_text = text.lower()

    text = text.replace("(at)", "@").replace(" at ", "@")
    text = text.replace("(dot)", ".").replace(" dot ", ".")

    # -----------------------
    # Initialize Intelligence Structure
    # -----------------------
    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phones", [])
    intelligence.setdefault("links", [])
    intelligence.setdefault("bankAccounts", [])
    intelligence.setdefault("otpCodes", [])
    intelligence.setdefault("ifscCodes", [])
    intelligence.setdefault("emails", [])
    intelligence.setdefault("suspiciousDomains", [])
    intelligence.setdefault("scamCategorySignals", [])
    intelligence.setdefault("riskScore", 0)

    # -----------------------
    # UPI ID Detection
    # -----------------------
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
    upis = re.findall(upi_pattern, text)

    for u in upis:
        if u not in intelligence["upiIds"]:
            intelligence["upiIds"].append(u)
            intelligence["riskScore"] += 2

    # -----------------------
    # Phone Detection
    # -----------------------
    phone_pattern = r"(?:\+91[-\s–]?)?[6-9]\d{9}"
    phones = re.findall(phone_pattern, text)

    for p in phones:
        cleaned = re.sub(r"\D", "", p)[-10:]
        if cleaned not in intelligence["phones"]:
            intelligence["phones"].append(cleaned)
            intelligence["riskScore"] += 1

    # -----------------------
    # Bank Account Detection
    # -----------------------
    account_pattern = r"\b\d{12,18}\b"
    accounts = re.findall(account_pattern, text)

    for acc in accounts:
        if acc not in intelligence["bankAccounts"]:
            intelligence["bankAccounts"].append(acc)
            intelligence["riskScore"] += 3

    # -----------------------
    # OTP Detection
    # -----------------------
    if "otp" in lower_text:
        otp_pattern = r"\b\d{4,8}\b"
        otps = re.findall(otp_pattern, text)

        for o in otps:
            if o not in intelligence["otpCodes"]:
                intelligence["otpCodes"].append(o)
                intelligence["riskScore"] += 3

    # -----------------------
    # IFSC Detection
    # -----------------------
    ifsc_pattern = r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    ifsc_codes = re.findall(ifsc_pattern, text)

    for code in ifsc_codes:
        if code not in intelligence["ifscCodes"]:
            intelligence["ifscCodes"].append(code)
            intelligence["riskScore"] += 2

    # -----------------------
    # Link Detection
    # -----------------------
    link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"
    links = re.findall(link_pattern, text)

    for l in links:
        if l not in intelligence["links"]:
            intelligence["links"].append(l)
            intelligence["riskScore"] += 2

            # Extract suspicious domain
            domain_match = re.search(r"https?://([^/]+)", l)
            if domain_match:
                domain = domain_match.group(1)
                if domain not in intelligence["suspiciousDomains"]:
                    intelligence["suspiciousDomains"].append(domain)

    # -----------------------
    # Email Detection
    # -----------------------
    email_pattern = r"\b[a-zA-Z0-9._%+-]{2,}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b"
    emails = re.findall(email_pattern, text)

    common_suspicious_domains = [
        "gmail-security.com",
        "secure-bank.net",
        "verify-update.com"
    ]

    for e in emails:
        if e not in intelligence["emails"]:
            intelligence["emails"].append(e)
            intelligence["riskScore"] += 1

    # -----------------------
    # Scam Category Signals
    # -----------------------

    if "otp" in lower_text:
        intelligence["scamCategorySignals"].append("otp_scam")

    if "cashback" in lower_text or "winner" in lower_text:
        intelligence["scamCategorySignals"].append("reward_scam")

    if "click" in lower_text or "http" in lower_text:
        intelligence["scamCategorySignals"].append("phishing")

    if "bank" in lower_text or "account" in lower_text:
        intelligence["scamCategorySignals"].append("bank_fraud")

    if "email" in lower_text:
        if "email_collection_attempt" not in intelligence["scamCategorySignals"]:
            intelligence["scamCategorySignals"].append("email_collection_attempt")
            intelligence["riskScore"] += 1

    # Remove duplicates
    intelligence["scamCategorySignals"] = list(
        set(intelligence["scamCategorySignals"])
    )
