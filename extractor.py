import re


def extract(message: str, intelligence: dict):
    if not message or not isinstance(message, str):
        return

    # Normalize text
    text = message.strip()
    lower_text = text.lower()

    # -----------------------
    # Initialize keys safely
    # -----------------------
    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phones", [])
    intelligence.setdefault("links", [])
    intelligence.setdefault("bankAccounts", [])
    intelligence.setdefault("otpCodes", [])
    intelligence.setdefault("ifscCodes", [])
    intelligence.setdefault("emails", [])

    # -----------------------
    # UPI ID Detection
    # -----------------------
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
    upis = re.findall(upi_pattern, text)
    for u in upis:
        if u not in intelligence["upiIds"]:
            intelligence["upiIds"].append(u)

    # -----------------------
    # Phone Number Detection (Indian +91 supported)
    # -----------------------
    phone_pattern = r"(?:\+91[-\s–]?)?[6-9]\d{9}"
    phones = re.findall(phone_pattern, text)
    for p in phones:
        cleaned = re.sub(r"\D", "", p)[-10:]  # keep last 10 digits
        if cleaned not in intelligence["phones"]:
            intelligence["phones"].append(cleaned)

    # -----------------------
    # Bank Account Detection (12–18 digit numbers)
    # -----------------------
    account_pattern = r"\b\d{12,18}\b"
    accounts = re.findall(account_pattern, text)
    for acc in accounts:
        if acc not in intelligence["bankAccounts"]:
            intelligence["bankAccounts"].append(acc)

    # -----------------------
    # OTP Detection (4–8 digits near OTP keyword)
    # -----------------------
    if "otp" in lower_text:
        otp_pattern = r"\b\d{4,8}\b"
        otps = re.findall(otp_pattern, text)
        for o in otps:
            if o not in intelligence["otpCodes"]:
                intelligence["otpCodes"].append(o)

    # -----------------------
    # IFSC Detection
    # -----------------------
    ifsc_pattern = r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    ifsc_codes = re.findall(ifsc_pattern, text)
    for code in ifsc_codes:
        if code not in intelligence["ifscCodes"]:
            intelligence["ifscCodes"].append(code)

    # -----------------------
    # Link Detection
    # -----------------------
    link_pattern = r"(https?://[^\s]+)"
    links = re.findall(link_pattern, text)
    for l in links:
        if l not in intelligence["links"]:
            intelligence["links"].append(l)

    # -----------------------
    # Email Detection
    # -----------------------
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    emails = re.findall(email_pattern, text)
    for e in emails:
        if e not in intelligence["emails"]:
            intelligence["emails"].append(e)
