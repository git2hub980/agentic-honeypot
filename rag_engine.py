import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("scam_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["fraudster"] for item in data]

embeddings = model.encode(texts)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))


def get_rag_reply(user_message, language):
    query_embedding = model.encode([user_message])
    distances, indices = index.search(query_embedding, k=3)

    best_match = None

    for idx in indices[0]:
     if data[idx]["language"] == language:
        best_match = data[idx]
        break

    if not best_match:
      return "Please wait..."

    return best_match["human_reply"]


    if matched_item["language"] == language:
        return matched_item["human_reply"]

    return "Please wait..."
