import re


def extract(message: str, intelligence: dict):
    if not message:
        return

    text = message.lower()

    # -----------------------
    # Initialize keys safely
    # -----------------------
    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phones", [])
    intelligence.setdefault("links", [])
    intelligence.setdefault("bankAccounts", [])
    intelligence.setdefault("otpCodes", [])
    intelligence.setdefault("ifscCodes", [])

    # -----------------------
    # UPI ID Detection
    # -----------------------
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
    upis = re.findall(upi_pattern, message)
    for u in upis:
        if u not in intelligence["upiIds"]:
            intelligence["upiIds"].append(u)

    # -----------------------
    # Phone Number Detection (10 digit Indian)
    # -----------------------
    phone_pattern = r"\b[6-9]\d{9}\b"
    phones = re.findall(phone_pattern, message)
    for p in phones:
        if p not in intelligence["phones"]:
            intelligence["phones"].append(p)

    # -----------------------
    # Bank Account Detection (12–18 digit numbers)
    # -----------------------
    account_pattern = r"\b\d{12,18}\b"
    accounts = re.findall(account_pattern, message)
    for acc in accounts:
        if acc not in intelligence["bankAccounts"]:
            intelligence["bankAccounts"].append(acc)

    # -----------------------
    # OTP Detection (4–8 digits near OTP keyword)
    # -----------------------
    if "otp" in text:
        otp_pattern = r"\b\d{4,8}\b"
        otps = re.findall(otp_pattern, message)
        for o in otps:
            if o not in intelligence["otpCodes"]:
                intelligence["otpCodes"].append(o)

    # -----------------------
    # IFSC Detection
    # -----------------------
    ifsc_pattern = r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    ifsc_codes = re.findall(ifsc_pattern, message)
    for code in ifsc_codes:
        if code not in intelligence["ifscCodes"]:
            intelligence["ifscCodes"].append(code)

    # -----------------------
    # Link Detection
    # -----------------------
    link_pattern = r"(https?://[^\s]+)"
    links = re.findall(link_pattern, message)
    for l in links:
        if l not in intelligence["links"]:
            intelligence["links"].append(l)
