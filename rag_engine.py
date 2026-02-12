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


def get_rag_reply(user_message, language):
    query_embedding = model.encode([user_message])
    distances, indices = index.search(query_embedding, k=3)

    for idx in indices[0]:
        matched_item = clean_data[idx]
        if matched_item["language"] == language:
            return matched_item["human_reply"]

    return "Please wait..."
