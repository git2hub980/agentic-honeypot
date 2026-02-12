import re

def extract(message, intelligence):
    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phones", [])
    intelligence.setdefault("links", [])
    intelligence.setdefault("bankAccounts", [])

    # UPI IDs (stricter)
    upi_matches = re.findall(
        r"\b[a-zA-Z0-9._-]{3,}@[a-zA-Z]{2,}\b", message
    )

    # Phone numbers (10 digits, not part of larger number)
    phone_matches = re.findall(
        r"(?<!\d)\d{10}(?!\d)", message
    )

    # Links
    link_matches = re.findall(
        r"https?://[^\s]+", message
    )

    # Bank accounts (11–18 digits ONLY to avoid 10-digit phone clash)
    bank_matches = re.findall(
        r"(?<!\d)\d{11,18}(?!\d)", message
    )

    # Deduplicate
    intelligence["upiIds"] = list(set(intelligence["upiIds"] + upi_matches))
    intelligence["phones"] = list(set(intelligence["phones"] + phone_matches))
    intelligence["links"] = list(set(intelligence["links"] + link_matches))
    intelligence["bankAccounts"] = list(set(intelligence["bankAccounts"] + bank_matches))
