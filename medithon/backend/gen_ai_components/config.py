import os
from pathlib import Path
from dotenv import load_dotenv


# =============================================================================
# PATH CONFIG
# =============================================================================

BASE_DIR = Path(__file__).parent

ENV_PATH = BASE_DIR / ".env"
VECTOR_DIR = BASE_DIR / "Vector"


# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================

# Load .env file
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    # fallback: load from default search path
    load_dotenv()


# =============================================================================
# API KEYS
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found. Please set it in the .env file.")


# =============================================================================
# MODEL CONFIG
# =============================================================================

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


# =============================================================================
# CHROMA VECTOR DB PATHS
# =============================================================================

CHROMA_DRUGS_MASTER_PATH = VECTOR_DIR / "chroma_drugs_master"
CHROMA_COMPARISON_PATH = VECTOR_DIR / "chroma_comparison"
CHROMA_INTERACTIONS_PATH = VECTOR_DIR / "chroma_interactions"
CHROMA_REIMBURSEMENT_PATH = VECTOR_DIR / "chroma_reimbursement"


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """
You are a Medical Representative AI Assistant designed for healthcare professionals.

You provide ONLY evidence-based drug information using the available databases.

Your responsibilities:
- Explain drug mechanism of action (MoA), indications, dosing, contraindications, and safety.
- Check drug-drug interactions using retrieved data.
- Provide reimbursement and insurance coverage information when available.
- Compare drugs when asked.

STRICT RULES:
1. Always use tool retrieval outputs when answering medical questions.
2. Never hallucinate drug facts.
3. If information is missing, explicitly say: "Data not found in database."
4. Do NOT diagnose patients.
5. Do NOT recommend a final treatment plan.
6. Provide professional, structured medical answers.
7. Highlight CRITICAL interactions clearly.
8. Always include a disclaimer at the end.
"""


# =============================================================================
# USER PROMPT TEMPLATE
# =============================================================================

USER_PROMPT_TEMPLATE = """
Doctor Query:
{query}

Instructions:
- Use retrieved tool outputs only.
- If query requires interactions, ensure interaction checking is included.
- If reimbursement is requested, include coverage/cost details if present.
- If the patient is diabetic, ask which diabetic medications they take before concluding interaction safety.
- Format response professionally with bullet points and headings.
"""
