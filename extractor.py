import re

def extract(message, intelligence):
    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phones", [])
    intelligence.setdefault("links", [])

    intelligence["upiIds"].extend(re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", message))
    intelligence["phones"].extend(re.findall(r"\b\d{10}\b", message))
    intelligence["links"].extend(re.findall(r"https?://\S+", message))
