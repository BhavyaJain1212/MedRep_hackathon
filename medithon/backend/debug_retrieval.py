from gen_ai_components.combined_chaining import refinement_chain, parallel_retriever, combine_retrieved_docs

query = "price of ibuprofen"
print(f"🔍 Debugging Query: '{query}'")

# 1. Refinement
refined = refinement_chain.invoke({"user_query": query, "history": []})
print(f"✅ Refined Query: '{refined}'")

# 2. Retrieval
print("\n📥 Checking DB Counts...")
from gen_ai_components.combined_chaining import db_drugs, db_reimbursement, db_interactions, db_comparisons

print(f"Drugs Count: {db_drugs._collection.count()}")
print(f"Reimbursement Count: {db_reimbursement._collection.count()}")
print(f"Interactions Count: {db_interactions._collection.count()}")
print(f"Comparisons Count: {db_comparisons._collection.count()}")

print("\n📥 Retrieving Documents...")
refined = refinement_chain.invoke({"user_query": query, "history": []}) # Re-run refinement
docs_map = parallel_retriever.invoke(refined)

print("\n--- REIMBURSEMENT DB RESULTS ---")
for i, doc in enumerate(docs_map["reimbursement"]):
    print(f"\n[Doc {i+1}] {doc.page_content[:500]}...")

print("\n--- DRUGS MASTER DB RESULTS ---")
for i, doc in enumerate(docs_map["drugs"]):
    print(f"\n[Doc {i+1}] {doc.page_content[:500]}...")

print("\n--- COMBINED CONTEXT PREVIEW ---")
context = combine_retrieved_docs(docs_map)
print(context[:1000])
