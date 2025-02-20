import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from constants import INDEX_PATH, MESSAGES_DB_PATH, FAISS_DIMENSION
from utils import get_session_directory

# Embedding model
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def load_db(user_id, session_id):
    index = faiss.IndexFlatL2(FAISS_DIMENSION)
    messages_db = []
    index_path = get_session_directory(user_id, session_id) + INDEX_PATH
    messages_db_path = get_session_directory(user_id, session_id) + MESSAGES_DB_PATH

    # Embeddings index
    if not os.path.exists(index_path):
        faiss.write_index(index, index_path)
    index = faiss.read_index(index_path)

    # Messages database
    if not os.path.exists(messages_db_path):
        with open(messages_db_path, 'w'):
            pass
    with open(messages_db_path, 'r') as f:
        messages_db = f.read().splitlines()
    
    return index, messages_db

def save_db(session):
    # Save the embeddings index
    index_path = get_session_directory(session.user_id, session.session_id) + INDEX_PATH
    messages_db_path = get_session_directory(session.user_id, session.session_id) + MESSAGES_DB_PATH

    faiss.write_index(session.index, index_path)

    # Save the messages database
    with open(messages_db_path, 'w') as f:
        f.write('\n'.join(session.messages_db))


def add_message_to_db(session, message):
    index, messages_db = session.index, session.messages_db
    
    message_embedding = embedding_model.encode(message)
    index.add(np.array([message_embedding]))
    messages_db.append(message)

    save_db(session)


def search_db(session, query, k=3):
    index, messages_db = session.index, session.messages_db

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
