import requests
import json
import re
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from ddgs import DDGS


# =============================================================================
# Utility Functions
# =============================================================================

def safe_get(url: str, params: dict = None, timeout: int = 10) -> Dict:
    """Safe GET request with JSON fallback."""
    try:
        res = requests.get(url, params=params, timeout=timeout)
        if res.status_code == 200:
            try:
                return {"ok": True, "data": res.json()}
            except Exception:
                return {"ok": True, "data": res.text}
        return {"ok": False, "status_code": res.status_code, "error": res.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def ddg_search(query: str, max_results: int = 5) -> List[Dict]:
    """DuckDuckGo search results."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "href": r.get("href"),
                    "body": r.get("body")
                })
    except Exception as e:
        return [{"error": str(e)}]
    return results


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extract sentences containing key medical words."""
    if not text:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    extracted = []
    for s in sentences:
        for kw in keywords:
            if kw.lower() in s.lower():
                extracted.append(s.strip())
                break
    return extracted[:15]


# =============================================================================
# 1. RxNorm API (drug ID mapping)
# =============================================================================

def get_rxnorm_rxcui(drug_name: str) -> Dict:
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    params = {"name": drug_name}
    res = safe_get(url, params=params)

    if not res["ok"]:
        return {"error": "RxNorm API failed", "details": res}

    try:
        rxcui = res["data"]["idGroup"]["rxnormId"][0]
        return {"drug_name": drug_name, "rxcui": rxcui}
    except Exception:
        return {"error": "No RxCUI found", "raw": res["data"]}


def get_rxnorm_properties(rxcui: str) -> Dict:
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json"
    res = safe_get(url)

    if not res["ok"]:
        return {"error": "RxNorm properties failed", "details": res}

    return res["data"]


def get_rxnorm_interactions(rxcui: str) -> Dict:
    url = "https://rxnav.nlm.nih.gov/REST/interaction/interaction.json"
    params = {"rxcui": rxcui}
    res = safe_get(url, params=params)

    if not res["ok"]:
        return {"error": "RxNorm interaction API failed", "details": res}

    return res["data"]


# =============================================================================
# 2. OpenFDA Drug Label API (warnings, contraindications, interactions)
# =============================================================================

def openfda_label_lookup(drug_name: str) -> Dict:
    url = "https://api.fda.gov/drug/label.json"
    params = {"search": f"openfda.generic_name:{drug_name}", "limit": 1}

    res = safe_get(url, params=params)
    if not res["ok"]:
        return {"error": "OpenFDA API failed", "details": res}

    try:
        result = res["data"]["results"][0]
        return {
            "drug_name": drug_name,
            "mechanism_of_action": result.get("mechanism_of_action", []),
            "indications_and_usage": result.get("indications_and_usage", []),
            "contraindications": result.get("contraindications", []),
            "drug_interactions": result.get("drug_interactions", []),
            "warnings_and_precautions": result.get("warnings_and_precautions", []),
        }
    except Exception:
        return {"error": "No OpenFDA results found", "raw": res["data"]}


# =============================================================================
# 3. PubChem API (chemical + pharmacology + targets)
# =============================================================================

def pubchem_lookup(drug_name: str) -> Dict:
    # Step 1: get CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
    cid_res = safe_get(cid_url)

    if not cid_res["ok"]:
        return {"error": "PubChem CID lookup failed", "details": cid_res}

    try:
        cid = cid_res["data"]["IdentifierList"]["CID"][0]
    except Exception:
        return {"error": "PubChem CID not found", "raw": cid_res["data"]}

    # Step 2: get description / pharmacology section
    desc_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
    desc_res = safe_get(desc_url)

    if not desc_res["ok"]:
        return {"error": "PubChem description failed", "details": desc_res}

    return {
        "drug_name": drug_name,
        "cid": cid,
        "raw_pubchem": desc_res["data"]
    }


def extract_pubchem_mechanism(pubchem_json: Dict) -> Dict:
    """Extract relevant pharmacology / mechanism-like text from PubChem record."""
    keywords = [
        "mechanism", "inhibitor", "receptor", "enzyme",
        "bind", "block", "agonist", "antagonist",
        "pathway", "inhibit", "target", "hormone"
    ]

    extracted = []

    try:
        sections = pubchem_json["Record"]["Section"]
        stack = list(sections)

        while stack:
            sec = stack.pop()
            if "Information" in sec:
                for info in sec["Information"]:
                    if "Value" in info and "StringWithMarkup" in info["Value"]:
                        for s in info["Value"]["StringWithMarkup"]:
                            extracted.extend(extract_keywords(s["String"], keywords))

            if "Section" in sec:
                stack.extend(sec["Section"])

    except Exception:
        return {"error": "Unable to extract mechanism from PubChem", "raw": pubchem_json}

    return {"mechanism_snippets": list(dict.fromkeys(extracted))[:20]}


# =============================================================================
# 4. Indian Sources (1mg / PharmEasy / CDSCO / NHP)
# =============================================================================

def india_drug_sources_search(drug_name: str) -> List[Dict]:
    query = f"{drug_name} mechanism of action site:1mg.com OR site:pharmeasy.in OR site:cdsco.gov.in OR site:nhp.gov.in"
    return ddg_search(query, max_results=6)


def india_price_sources_search(drug_name: str) -> List[Dict]:
    query = f"{drug_name} price site:1mg.com OR site:pharmeasy.in"
    return ddg_search(query, max_results=6)


# =============================================================================
# 5. Reimbursement Sources (Jan Aushadhi / NPPA / PMJAY)
# =============================================================================

def reimbursement_sources_search(drug_name: str) -> List[Dict]:
    query = f"{drug_name} site:janaushadhi.gov.in OR site:nppaindia.nic.in OR site:pmjay.gov.in OR site:hospitals.pmjay.gov.in"
    return ddg_search(query, max_results=8)


# =============================================================================
# TOOL FUNCTIONS (FINAL TO BE USED BY AGENT)
# =============================================================================

def drug_information_retrieval(drug_name: str) -> Dict:
    """
    Retrieves:
    - scientific MoA evidence from PubChem + OpenFDA
    - India drug sources for MoA-friendly explanation
    """
    output = {
        "tool": "drug_information_retrieval",
        "drug_name": drug_name,
        "sources_used": [],
        "scientific_mechanism": {},
        "clinical_label_info": {},
        "india_sources": []
    }

    # OpenFDA
    openfda = openfda_label_lookup(drug_name)
    if "error" not in openfda:
        output["clinical_label_info"] = openfda
        output["sources_used"].append("OpenFDA")

    # PubChem
    pubchem = pubchem_lookup(drug_name)
    if "error" not in pubchem:
        mechanism = extract_pubchem_mechanism(pubchem["raw_pubchem"])
        output["scientific_mechanism"] = mechanism
        output["sources_used"].append("PubChem")

    # Indian sources web search
    india_sources = india_drug_sources_search(drug_name)
    if india_sources:
        output["india_sources"] = india_sources
        output["sources_used"].append("DuckDuckGo India Sources")

    if not output["sources_used"]:
        output["error"] = "No sources returned data."

    return output


def drug_interaction_checker(drug_list: List[str]) -> Dict:
    """
    Interaction checking using:
    - RxNorm interactions
    - OpenFDA label interactions
    - PubMed fallback search
    """
    output = {
        "tool": "drug_interaction_checker",
        "drugs_checked": drug_list,
        "rxnorm_results": [],
        "openfda_results": [],
        "pubmed_evidence_links": [],
        "note": "RxNorm provides structured interactions. OpenFDA provides label text interactions."
    }

    # RxNorm interaction check (best structured)
    for drug in drug_list:
        rx = get_rxnorm_rxcui(drug)
        if "rxcui" in rx:
            interactions = get_rxnorm_interactions(rx["rxcui"])
            output["rxnorm_results"].append({
                "drug": drug,
                "rxcui": rx["rxcui"],
                "interactions": interactions
            })
        else:
            output["rxnorm_results"].append({
                "drug": drug,
                "error": "No RxCUI found"
            })

    # OpenFDA label interaction section
    for drug in drug_list:
        label = openfda_label_lookup(drug)
        output["openfda_results"].append(label)

    # PubMed fallback evidence search
    if len(drug_list) >= 2:
        query = f"{drug_list[0]} {drug_list[1]} drug interaction site:pubmed.ncbi.nlm.nih.gov"
        output["pubmed_evidence_links"] = ddg_search(query, max_results=5)

    return output


def comparative_analysis(drug_names: List[str]) -> Dict:
    """
    Compares drugs using:
    - PubChem extracted MoA
    - OpenFDA label differences
    - India sources
    """
    output = {
        "tool": "comparative_analysis",
        "drugs_compared": drug_names,
        "comparison_data": []
    }

    for drug in drug_names:
        info = drug_information_retrieval(drug)
        output["comparison_data"].append(info)

    return output


def reimbursement_navigator(drug_name: str) -> Dict:
    """
    Reimbursement / pricing support:
    - Jan Aushadhi availability
    - NPPA ceiling pricing sources
    - PMJAY scheme reference
    - Private insurance note
    """
    results = reimbursement_sources_search(drug_name)
    price_sources = india_price_sources_search(drug_name)

    return {
        "tool": "reimbursement_navigator",
        "drug_name": drug_name,
        "government_sources": results,
        "india_price_sources": price_sources,
        "note": (
            "India does not provide a single unified reimbursement API. "
            "Jan Aushadhi provides generic prices. NPPA provides ceiling prices. "
            "PMJAY provides treatment package coverage (not always drug-level). "
            "Private insurance reimbursement depends on insurer formulary + OPD coverage."
        )
    }


# =============================================================================
# TOOL ROUTER
# =============================================================================

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
