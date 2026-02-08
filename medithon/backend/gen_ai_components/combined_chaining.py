import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from gen_ai_components.refined_query import refined_query_prompt
from gen_ai_components.structured_output import MedicalResponse
from gen_ai_components.prompts import prompt, promt_user

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# MEMORY SETUP
# =============================================================================

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Returns the chat history for a given session ID."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def format_chat_history(history):
    """Formats chat history list into a string for the refinement prompt."""
    return "\n".join([f"{msg.type}: {msg.content}" for msg in history])


# =============================================================================
# 1. SETUP: API KEY & EMBEDDINGS
# =============================================================================

# Initialize Embedding Model (Must match what you used to create the vector stores)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

print("🔄 Loading Vector Databases...")

# =============================================================================
# 2. LOAD YOUR 4 SPECIFIC VECTOR STORES
# =============================================================================

# DB 1: Drugs Master (General Info)
# Path: ./Vector/Vector_drugs_master
db_drugs = Chroma(persist_directory="./Vector/Vector_drugs_master", embedding_function=embedding_model)
retriever_drugs = db_drugs.as_retriever(search_kwargs={"k": 2})

# DB 2: Interactions (The specific interaction matrix)
# Path: ./Vector/Vector_interactions
db_interactions = Chroma(persist_directory="./Vector/Vector_interactions", embedding_function=embedding_model)
retriever_interactions = db_interactions.as_retriever(search_kwargs={"k": 2})

# DB 3: Reimbursement (CGHS/Pricing)
# Path: ./Vector/Vector_reimbursement
db_reimbursement = Chroma(persist_directory="./Vector/Vector_reimbursement", embedding_function=embedding_model)
retriever_reimbursement = db_reimbursement.as_retriever(search_kwargs={"k": 2})

# DB 4: Comparisons (Safety & Alternatives)
# Path: ./Vector/Vector_comparisons
db_comparisons = Chroma(persist_directory="./Vector/Vector_comparisons", embedding_function=embedding_model)
retriever_comparisons = db_comparisons.as_retriever(search_kwargs={"k": 2})

print("✅ All 4 Databases Loaded.")

# =============================================================================
# 3. THE "CONTEXT MERGER"
# =============================================================================

def combine_retrieved_docs(docs_map):
    """Combines documents from all 4 databases into one structured context string."""
    combined_text = ""
    
    # 1. Drugs Master Data
    combined_text += "\n--- DRUG MASTER DATA ---\n"
    combined_text += "\n".join([doc.page_content for doc in docs_map["drugs"]])
    
    # 2. Interaction Data
    combined_text += "\n--- INTERACTION ALERTS ---\n"
    combined_text += "\n".join([doc.page_content for doc in docs_map["interactions"]])
    
    # 3. Reimbursement Data
    combined_text += "\n--- REIMBURSEMENT & PRICING ---\n"
    combined_text += "\n".join([doc.page_content for doc in docs_map["reimbursement"]])
    
    # 4. Comparison/Safety Data
    combined_text += "\n--- COMPARISONS & SAFETY ---\n"
    combined_text += "\n".join([doc.page_content for doc in docs_map["comparisons"]])
    
    return combined_text

# =============================================================================
# 4. BUILD THE CHAIN WITH STRUCTURED OUTPUT
# =============================================================================

# LCEL Parallel Execution (Keys must match the function above)
parallel_retriever = RunnableParallel({
    "drugs": retriever_drugs,
    "interactions": retriever_interactions,
    "reimbursement": retriever_reimbursement,
    "comparisons": retriever_comparisons
})

llm = ChatOpenAI(model="gpt-4o", temperature=0) # GPT-4 is best for medical logic

# --- Step 1: Query Refinement Chain ---
refinement_chain = (
    {
        "user_query": lambda x: x["user_query"],
        "chat_history": lambda x: format_chat_history(x["history"])
    }
    | refined_query_prompt
    | llm
    | StrOutputParser()
)

# --- Step 2: Main RAG Chain ---
# Uses the refined query for both retrieval and final generation
structured_llm = llm.with_structured_output(MedicalResponse)

rag_chain = (
    # 1. Refine the query
    RunnablePassthrough.assign(refined_query=refinement_chain)
    
    # 2. Retrieve context based on REFINED query
    | RunnableParallel({
        "context": (lambda x: x["refined_query"]) | parallel_retriever | combine_retrieved_docs,
        "query": lambda x: x["refined_query"], # Pass refined query to generation logic for prompt
        "history": lambda x: x["history"] # Pass history through
    })
    
    # 3. Generate Answer
    | prompt
    | structured_llm
)

chain = rag_chain
chain_user = promt_user | structured_llm

# =============================================================================
# 6. EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("\n🏥 DMR Multi-DB Agent Online (Structured Output).\n")

    # Test Query
    user_query = "Can I prescribe Metformin to a heart failure patient who is also on Enalapril? Is it covered by CGHS?"

    print(f"👨‍⚕️ Query: {user_query}\n")
    print("🤖 DMR Response:\n")

    # Manual History Management for Testing
    session_id = "test_manual_session"
    chat_history = get_session_history(session_id)
    
    # Invoke chain with explicit history
    # No Pydantic serialization issues because we handle history ourselves
    try:
        response = chain.invoke({
            "user_query": user_query,
            "history": chat_history.messages
        })
        
        # Add to history manually
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(response.summary) # Store summary in history

        # Display structured output
        print("=" * 70)
        print(f"SUMMARY: {response.summary}\n")
        
        if response.drug_information:
            print(f"DRUG INFO: {response.drug_information}\n")
        
        if response.interactions:
            print("INTERACTIONS:")
            for interaction in response.interactions:
                print(f"  - [{interaction.severity}] {', '.join(interaction.drugs_involved)}")
                print(f"    {interaction.description}")
                print(f"    → {interaction.recommendation}\n")
        
        if response.reimbursement:
            print(f"REIMBURSEMENT: {response.reimbursement.coverage_status}")
            if response.reimbursement.price_range:
                print(f"  Price: {response.reimbursement.price_range}")
            if response.reimbursement.restrictions:
                print(f"  Restrictions: {response.reimbursement.restrictions}")
            print()
        
        if response.safety_warnings:
            print("SAFETY WARNINGS:")
            for warning in response.safety_warnings:
                print(f"  - [{warning.category}] {warning.condition}")
                print(f"    {warning.description}\n")
        
        print(f"RECOMMENDATIONS: {response.recommendations}\n")
        
        if response.data_limitations:
            print(f"⚠️  DATA LIMITATIONS: {response.data_limitations}\n")
        
        if response.sources:
            print("SOURCES:")
            for src in response.sources:
                print(f"  - {src.database}: {src.snippet[:100]}...")
        
        print(f"\n📋 {response.disclaimer}")
        print("=" * 70)
        
        # Also print raw JSON for API integration
        print("\n\n📦 JSON OUTPUT:")
        import json
        print(json.dumps(response.model_dump(), indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

