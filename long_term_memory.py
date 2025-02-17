import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

INDEX_PATH = 'long_term_memory/index.faiss'
MESSAGES_DB_PATH = 'long_term_memory/messages_db.txt'

# Embedding models
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize FAISS index
dimension = 384  
index = faiss.IndexFlatL2(dimension)  
messages_db = []


def load_db():
    global index, messages_db

    # Embeddings index
    if not os.path.exists(INDEX_PATH):
        faiss.write_index(index, INDEX_PATH)
    index = faiss.read_index(INDEX_PATH)

    # Messages database
    if not os.path.exists(MESSAGES_DB_PATH):
        with open(MESSAGES_DB_PATH, 'w'):
            pass
    with open(MESSAGES_DB_PATH, 'r') as f:
        messages_db = f.read().splitlines()

def save_db():
    # Save the embeddings index
    faiss.write_index(index, INDEX_PATH)

    # Save the messages database
    with open(MESSAGES_DB_PATH, 'w') as f:
        f.write('\n'.join(messages_db))


def add_message_to_db(message):
    global index, messages_db
    
    message_embedding = embedding_model.encode(message)
    index.add(np.array([message_embedding]))
    messages_db.append(message)

    save_db()


def search_db(query, k=3):
    global index, messages_db

    if len(messages_db) == 0:
        return []

    query_embedding = embedding_model.encode(query)
    D, I = index.search(np.array([query_embedding]), k)

    results = []
    for i in I[0]:
        db_index = i
        if db_index == -1:
            break
        relevant_message = messages_db[db_index]
        results.append(relevant_message)

    return results
