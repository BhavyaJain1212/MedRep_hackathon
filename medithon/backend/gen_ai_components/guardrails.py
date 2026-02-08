import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# =============================================================================
# PATTERNS
# =============================================================================

PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"developer message",
    r"jailbreak",
    r"bypass safety",
    r"act as",
    r"pretend you are",
    r"you are now",
    r"do anything now",
    r"reveal your rules",
    r"show hidden prompt",
    r"disable guardrails",
]

NON_MEDICAL_PATTERNS = [
    r"bitcoin",
    r"stock price",
    r"movie",
    r"song",
    r"politics",
    r"game",
]

CREATIVE_PATTERNS = [
    r"poem",
    r"joke",
    r"story",
    r"song",
    r"rap",
    r"lyrics",
    r"haiku",
    r"dialogue",
    r"character",
]

PATIENT_SPECIFIC_PATTERNS = [
    r"\bmy patient\b",
    r"\bmy father\b",
    r"\bmy mother\b",
    r"\bmy friend\b",
    r"\bI am taking\b",
    r"\bmy symptoms\b",
    r"\bshould I take\b",
    r"\bcan I take\b",
    r"\bdose for me\b",
]

DIAGNOSIS_PATTERNS = [
    r"diagnose",
    r"what disease do I have",
    r"am I suffering from",
]

DISEASE_PATTERNS = [
    r"\bdiabetes\b",
    r"\bhypertension\b",
    r"\basthma\b",
    r"\bheart\b",
    r"\bkidney\b",
    r"\bliver\b",
    r"\bcancer\b",
]

MEDICATION_INDICATORS = [
    r"\bmg\b",
    r"\btablet\b",
    r"\bcapsule\b",
    r"\binjection\b",
    r"\bdose\b",
    r"\bmetformin\b",
    r"\binsulin\b",
    r"\bparacetamol\b",
    r"\baspirin\b",
]

# =============================================================================
# GUARDRAIL RESPONSES
# =============================================================================

def block(reason: str, category: str):
    return {
        "status": "blocked",
        "category": category,
        "message": (
            "⚠️ I can’t help with this request.\n\n"
            f"Reason: {reason}\n\n"
            "This assistant provides factual, professional medical information only."
        )
    }

def clarify(reason: str):
    return {
        "status": "clarification_required",
        "message": reason
    }

# =============================================================================
# INPUT GUARDRAILS
# =============================================================================

class InputGuardrails:

    def detect(self, patterns, query):
        return any(re.search(p, query) for p in patterns)

    def detect_creative_medical_conflict(self, query: str) -> bool:
        q = query.lower()
        creative = self.detect(CREATIVE_PATTERNS, q)
        medical = self.detect(MEDICATION_INDICATORS + DISEASE_PATTERNS, q)
        return creative and medical

    def run(self, query: str) -> Dict[str, Any]:
        q = query.lower().strip()

        # ✅ Allow greetings
        if q in ["hi", "hello", "hello doctor", "hi doctor"]:
            return {"status": "allowed"}

        # 🚫 Prompt injection
        if self.detect(PROMPT_INJECTION_PATTERNS, q):
            return block("Prompt injection attempt detected.", "prompt_injection")

        # 🚫 Creative + medical conflict
        if self.detect_creative_medical_conflict(q):
            return block(
                "Creative or entertainment-style requests involving medicines are not allowed.",
                "creative_medical_conflict"
            )

        # 🚫 Out of scope
        if self.detect(NON_MEDICAL_PATTERNS, q):
            return block("Non-medical query detected.", "out_of_scope")

        # 🚫 Diagnosis
        if self.detect(DIAGNOSIS_PATTERNS, q):
            return block("Diagnosis requests are not permitted.", "diagnosis_blocked")

        # ⚠️ Patient-specific → clarify
        if self.detect(PATIENT_SPECIFIC_PATTERNS, q):
            return clarify(
                "Please consult a qualified doctor. I can only provide general medical information."
            )

        return {"status": "allowed"}

# =============================================================================
# OUTPUT GUARDRAILS
# =============================================================================

class OutputGuardrails:

    DISCLAIMER = (
        "\n\n---\n"
        "⚠️ Disclaimer: This information is for educational purposes only "
        "and does not replace professional medical advice."
    )

    def run(self, response: str, tool_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:

        # 🚫 Hallucination prevention
        if not tool_outputs:
            return block(
                "No verified medical data was retrieved to support this response.",
                "hallucination_blocked"
            )

        # ✅ Enforce disclaimer
        if "Disclaimer" not in response:
            response += self.DISCLAIMER

        return {
            "status": "allowed",
            "safe_response": response
        }

# =============================================================================
# AUDIT LOGGER
# =============================================================================

class AuditLogger:

    def __init__(self, logfile="audit_log.jsonl"):
        self.logfile = logfile

    def log(self, query: str, response: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": response
        }
        with open(self.logfile, "a") as f:
            f.write(json.dumps(entry) + "\n")

# =============================================================================
# FULL FRAMEWORK
# =============================================================================

class GuardrailsFramework:

    def __init__(self, audit_logfile: str = "audit_log.jsonl"):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.logger = AuditLogger()

    def validate_input(self, query: str):
        return self.input_guardrails.run(query)

    def validate_output(self, response: str, tool_outputs: List[Dict[str, Any]]):
        return self.output_guardrails.run(response, tool_outputs)

    def audit(self, query: str, response: str):
        self.logger.log(query, response)