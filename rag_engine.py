import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("scam_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
clean_data = []

for item in data:
    # Case 1: simple structure
    if "fraudster" in item:
        texts.append(item["fraudster"])
        clean_data.append(item)

    elif "fraudster_message" in item:
        texts.append(item["fraudster_message"])
        clean_data.append({
            "language": item["language"],
            "fraudster": item["fraudster_message"],
            "human_reply": item["human_reply"]
        })

    # Case 2: conversation list
    elif "conversation" in item:
        for convo in item["conversation"]:
            fraud_msg = convo.get("fraudster") or convo.get("fraudster_message")
            if fraud_msg:
                texts.append(fraud_msg)
                clean_data.append({
                    "language": item["language"],
                    "fraudster": fraud_msg,
                    "human_reply": convo["human_reply"]
                })

# Generate embeddings
embeddings = model.encode(texts)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

def normalize_lang(lang):
    mapping = {
        "en": "english",
        "hi": "hindi",
        "hinglish":"hinglish",
        "ta": "tamil",
        "te": "telugu",
        "ml": "malayalam",
        "mr": "marathi",
        "gu": "gujarati",
        "kn": "kannada"
    }
    return mapping.get(lang.lower(), lang.lower())


def get_rag_reply(user_message, language):
    query_embedding = model.encode([user_message])
    distances, indices = index.search(query_embedding, k=5)

    normalized_language = normalize_lang(language)

    # 1️⃣ Try language match first
    for idx in indices[0]:
        matched_item = clean_data[idx]
        if normalize_lang(matched_item["language"]) == normalized_language:
            return matched_item["human_reply"]

    # 2️⃣ Fallback: return top similarity
    best_idx = indices[0][0]
    return clean_data[best_idx]["human_reply"]

