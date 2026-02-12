import json
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(BASE_DIR, "scam_dataset.json")

with open(dataset_path, "r", encoding="utf-8") as f:
    data = json.load(f)


texts = [item.get("fraudster", "") for item in data]


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


    
