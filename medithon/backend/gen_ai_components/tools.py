from pathlib import Path
from typing import Dict, List, Any

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import OPENAI_API_KEY

# -------------------------------
# Paths
# -------------------------------
BASE_PATH = Path(__file__).parent
VECTOR_PATH = BASE_PATH / "Vector"

# -------------------------------
# Embedding Model
# -------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY,
)

# -------------------------------
# Load Chroma Vectorstores
# -------------------------------
chroma_drugs_mastery = Chroma(
    persist_directory=str(VECTOR_PATH / "Vector_drugs_master"),
    embedding_function=embedding_model,
)

chroma_comparisons = Chroma(
    persist_directory=str(VECTOR_PATH / "Vector_comparisons"),
    embedding_function=embedding_model,
)

chroma_interactions = Chroma(
    persist_directory=str(VECTOR_PATH / "Vector_interactions"),
    embedding_function=embedding_model,
)

chroma_reimbursements = Chroma(
    persist_directory=str(VECTOR_PATH / "Vector_reimbursement"),
    embedding_function=embedding_model,
)

# ============================================================================
# TOOL EXECUTION ROUTER
# ============================================================================


def execute_tool(tool_name: str, tool_input: Dict) -> Any:
    if tool_name == "drug_information_retrieval":
        return drug_information_retrieval(tool_input["drug_name"])

    elif tool_name == "comparative_analysis":
        return comparative_analysis(tool_input["drug_names"])

    elif tool_name == "drug_interaction_checker":
        return drug_interaction_checker(tool_input["drug_list"])

    elif tool_name == "reimbursement_navigator":
        return reimbursement_navigator(tool_input["drug_name"])

    else:
        return {"error": f"Unknown tool: {tool_name}"}


# ============================================================================
# TOOL FUNCTIONS (VECTOR DB ONLY)
# ============================================================================


def drug_information_retrieval(drug_name: str, k: int = 5) -> Dict:
    """
    Retrieve drug information from chroma_drugs_mastery using similarity search.
    """
    results = chroma_drugs_mastery.similarity_search(drug_name, k=k)

    if not results:
        return {"error": f"No drug information found for: {drug_name}"}

    return {
        "query": drug_name,
        "top_matches": [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ],
    }
    

def comparative_analysis(drug_names: List[str], k: int = 5) -> Dict:
    """
    Retrieve comparison data from chroma_comparisons.
    """
    query = " comparison between ".join(drug_names)
    results = chroma_comparisons.similarity_search(query, k=k)

    if not results:
        return {"error": f"No comparison data found for: {drug_names}"}

    return {
        "query": query,
        "drugs_compared": drug_names,
        "top_matches": [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ],
    }


def drug_interaction_checker(drug_list: List[str], k: int = 5) -> Dict:
    """
    Retrieve interaction information from chroma_interactions.
    """
    query = " interaction between " + " and ".join(drug_list)
    results = chroma_interactions.similarity_search(query, k=k)

    if not results:
        return {
            "status": "no_interactions_found",
            "query": query,
            "drugs_checked": drug_list,
        }

    return {
        "status": "interactions_found",
        "query": query,
        "drugs_checked": drug_list,
        "top_matches": [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ],
    }


def reimbursement_navigator(drug_name: str, k: int = 5) -> Dict:
    """
    Retrieve reimbursement information from chroma_reimbursements.
    """
    query = f"reimbursement coverage insurance information for {drug_name}"
    results = chroma_reimbursements.similarity_search(query, k=k)

    if not results:
        return {"error": f"No reimbursement information found for: {drug_name}"}

    return {
        "query": query,
        "drug_name": drug_name,
        "top_matches": [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ],
    }
