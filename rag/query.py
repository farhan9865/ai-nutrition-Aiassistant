from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

DB_PATH = "rag/vector_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True,
)

def search_docs(query: str, k: int = 4):
    return db.similarity_search(query, k=k)

