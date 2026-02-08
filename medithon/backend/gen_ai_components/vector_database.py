import os
from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# -------------------------------
# 0. Load Environment Variables
# -------------------------------
load_dotenv()  # loads .env from current or parent directories

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file")

print("✅ OpenAI API key loaded")

# -------------------------------
# 1. Load JSON File
# -------------------------------
loader = JSONLoader(
    file_path="../data/reimbursement.json",
    jq_schema=".",
    text_content=False
)

docs = loader.load()
print("Loaded documents:", len(docs))
print("Sample document:\n", docs[0].page_content)

# -------------------------------
# 2. Chunk Documents
# -------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5300,
    chunk_overlap=500
)

chunks = text_splitter.split_documents(docs)
print("\nTotal chunks created:", len(chunks))
print("Sample chunk:\n", chunks[0].page_content)

# -------------------------------
# 3. Create OpenAI Embeddings
# -------------------------------
openai_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)

# -------------------------------
# 4. Store in ChromaDB
# -------------------------------
vectorstore_comparisons = Chroma.from_documents(
    documents=chunks,
    embedding=openai_embeddings,
    persist_directory="./Vector/Vector_reimbursemnt"
)

vectorstore_comparisons.persist()
print("\n✅ Vector database created and stored in ./Vector")

# -------------------------------
# 5. Test Retrieval
# -------------------------------
retriever = vectorstore_comparisons.as_retriever(search_kwargs={"k": 1})

query = "is Paracetamol included and what is the cost"
results = retriever.invoke(query)

print("\n🔍 Top Results:")
for i, res in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(res.page_content)

print("\n🚀 The vector store is ready")
