import re

def extract(text, intel):
    upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text)
    links = re.findall(r"https?://\S+", text)
    phones = re.findall(r"\+?\d{10,13}", text)

    intel["upiIds"] += upi
    intel["links"] += links
    intel["phones"] += phones
