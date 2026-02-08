from typing import List, Optional
from pydantic import BaseModel, Field

class DrugInteraction(BaseModel):
    """Information about a drug-drug interaction"""
    drugs_involved: List[str] = Field(description="Names of drugs involved in the interaction")
    severity: str = Field(description="Severity level: CRITICAL, MAJOR, MODERATE, or MINOR")
    description: str = Field(description="Description of the interaction and clinical significance")
    recommendation: str = Field(description="Clinical recommendation or action to take")

class ReimbursementInfo(BaseModel):
    """Reimbursement and pricing information"""
    coverage_status: str = Field(description="Coverage status (e.g., 'Covered by CGHS', 'Not covered', 'Partial coverage')")
    price_range: Optional[str] = Field(default=None, description="Price range if available")
    restrictions: Optional[str] = Field(default=None, description="Any restrictions or requirements for coverage")

class SafetyWarning(BaseModel):
    """Safety warnings and contraindications"""
    category: str = Field(description="Category: CONTRAINDICATION, WARNING, PRECAUTION, or ADVERSE_EFFECT")
    condition: str = Field(description="Condition or situation this applies to")
    description: str = Field(description="Detailed safety information")

class SourceReference(BaseModel):
    """Reference to source documents used"""
    database: str = Field(description="Which database this came from (drugs_master, interactions, reimbursement, comparisons)")
    snippet: str = Field(description="Brief snippet of the relevant information")

class MedicalResponse(BaseModel):
    """Structured output for medical queries"""
    summary: str = Field(description="Brief summary of the response (2-3 sentences)")
    drug_information: Optional[str] = Field(default=None, description="General drug information (mechanism, indications, dosing) if relevant")
    interactions: List[DrugInteraction] = Field(default_factory=list, description="Drug interactions identified")
    reimbursement: Optional[ReimbursementInfo] = Field(default=None, description="Reimbursement information if queried")
    safety_warnings: List[SafetyWarning] = Field(default_factory=list, description="Safety warnings and contraindications")
    recommendations: Optional[str] = Field(default=None, description="Clinical recommendations based on the query")
    data_limitations: Optional[str] = Field(default=None, description="Any limitations in the available data")
    sources: List[SourceReference] = Field(default_factory=list, description="Sources used to generate this response")
    disclaimer: str = Field(
        default="This information is for healthcare professional reference only. Always verify with current medical literature and use clinical judgment.",
        description="Medical disclaimer"
    )