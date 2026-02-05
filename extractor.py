# extractor.py
import re

def extract(message, intelligence):
    upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", message)
    phones = re.findall(r"\b\d{10}\b", message)
    links = re.findall(r"https?://\S+", message)

    intelligence["upiIds"].extend(upi)
    intelligence["phones"].extend(phones)
    intelligence["links"].extend(links)
