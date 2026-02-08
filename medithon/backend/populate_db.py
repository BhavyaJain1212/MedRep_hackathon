import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# -------------------------------
# 0. Setup
# -------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
DATA_DIR = "./data"
VECTOR_DIR = "./Vector"

def create_vector_db(json_filename, vector_db_name, jq_schema=".", chunk_size=2000, chunk_overlap=200):
    print(f"\n🚀 Processing {json_filename} -> {vector_db_name}...")
    
    file_path = os.path.join(DATA_DIR, json_filename)
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    # 1. Load
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=jq_schema,
        text_content=False
    )
    docs = loader.load()
    print(f"   Loaded {len(docs)} documents.")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(docs)
    print(f"   Split into {len(chunks)} chunks.")

    # 3. Store
    persist_dir = os.path.join(VECTOR_DIR, vector_db_name)
    
    # Delete existing if any (to start fresh)
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        print(f"   Cleared existing DB at {persist_dir}")

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    print(f"✅ Created {vector_db_name}")

def append_csv_to_db(csv_filename, vector_db_name):
    print(f"\n➕ Appending {csv_filename} -> {vector_db_name}...")
    
    file_path = os.path.join(DATA_DIR, csv_filename)
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    # 1. Load
    loader = CSVLoader(file_path=file_path)
    docs = loader.load()
    print(f"   Loaded {len(docs)} CSV rows.")

    # 2. Store (Append to existing)
    persist_dir = os.path.join(VECTOR_DIR, vector_db_name)
    
    db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    db.add_documents(docs)
    print(f"✅ Appended CSV data to {vector_db_name}")

# -------------------------------
# EXECUTION
# -------------------------------
if __name__ == "__main__":
    print("🏥 Starting Vector Database Population...\n")
    
    # 1. Drugs Master
    create_vector_db("drugs_master.json", "Vector_drugs_master")
    
    # 2. Interactions
    create_vector_db("interactions.json", "Vector_interactions")
    
    # 3. Reimbursement (JSON + CSV)
    create_vector_db("reimbursement.json", "Vector_reimbursement")
    append_csv_to_db("jan_aushadhi_prices.csv", "Vector_reimbursement")
    
    # 4. Comparisons
    create_vector_db("comparisons.json", "Vector_comparisons")
    
    print("\n🎉 All databases populated successfully!")
