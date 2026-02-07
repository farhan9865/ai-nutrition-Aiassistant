from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_PATH = "data/pdfs/TASK_1_-_9.pdf"
DB_PATH = "rag/vector_db"

print("Loading PDF...")
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

print("Splitting text...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunks = splitter.split_documents(docs)

print("Embedding...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(chunks, embeddings)

db.save_local(DB_PATH)

print("Vector DB created at:", DB_PATH)
