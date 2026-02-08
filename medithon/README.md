# MedRep AI — Dataset Documentation

## Overview

This folder contains all structured data that powers MedRep AI's RAG pipeline. Data is loaded into ChromaDB at startup and queried alongside live OpenFDA API calls to generate responses.

**Total files:** 5 | **Total size:** ~67 KB | **Last updated:** Feb 2025

---

## File Descriptions

### 1. `drugs_master.json` (23.3 KB)

**Purpose:** Master reference mapping every drug to its identifiers, pricing, and formulary status.

| Field | Description |
|-------|-------------|
| `id` | Internal lookup key (e.g., `"paracetamol"`) |
| `generic_name` | Indian pharmacopeia name |
| `openfda_name` | US FDA name for API queries (e.g., Paracetamol → `"acetaminophen"`) |
| `category` | One of 6 categories (Pain, Antibiotics, Diabetes, Cardiovascular, GI, Respiratory) |
| `primary_strength` | Most common strength dispensed |
| `brands[]` | Common Indian brand names |
| `brand_mrp` | Verified brand MRP with source (PharmEasy, Apollo, etc.) |
| `jan_aushadhi_mrp` | Jan Aushadhi generic price for same drug |
| `savings_percent` | Pre-computed `(1 - jan_aushadhi/brand) × 100` for UI savings card |
| `cghs_codes[]` | CGHS formulary codes from MSO 2014 / VMS 2023 PDFs |
| `cghs_entry` | Human-readable CGHS listing description |
| `esic_status` | ESIC schedule status: `yes`, `fdc_only`, `kit_only`, `no`, or `not_verified` |
| `esic_detail` | Specific forms/strengths listed in ESIC dispensary schedule |
| `has_manual_comparisons` | `true` if this drug appears in `comparisons.json` (23/31) |
| `has_manual_interactions` | `true` if this drug appears in `interactions.json` (13/31) |

**Stats:**
- 31 drug entries across 6 categories
- 29/31 have verified brand MRPs with pharmacy sources
- 29/31 have ESIC status verified (2 remaining: doxycycline, ciprofloxacin)
- ESIC breakdown: 16 yes, 6 fdc_only, 1 kit_only, 6 no, 2 not_verified

**Sources:** PharmEasy, Apollo Pharmacy, 1mg, Medkart, MSO Formulary 2014, VMS Formulary 2023, ESIC dispensary drug schedule

---

### 2. `comparisons.json` (18.4 KB)

**Purpose:** Head-to-head drug comparison tables with evidence citations, used when doctors ask "which drug is better for X?"

**Structure:** 9 comparison tables, each with:
- `parameters[]` — rows comparing specific aspects (potency, side effects, cost, when to prefer)
- `evidence[]` — trial names and guideline references
- `key_takeaway` — one-line clinical summary

**Tables:**
| # | Comparison | Category |
|---|-----------|----------|
| 1 | Atorvastatin vs Rosuvastatin | Cardiovascular |
| 2 | Losartan vs Telmisartan | Cardiovascular |
| 3 | Amlodipine vs ARBs | Cardiovascular |
| 4 | Aspirin vs Clopidogrel vs DAPT | Cardiovascular |
| 5 | Pantoprazole vs Omeprazole vs Rabeprazole | Gastrointestinal |
| 6 | Amoxicillin vs Amox+Clav vs Azithromycin vs Cefixime | Antibiotics |
| 7 | Paracetamol vs Ibuprofen vs Diclofenac vs Aceclofenac | Pain Management |
| 8 | Metformin vs Glimepiride | Diabetes |
| 9 | Salbutamol vs Budesonide vs Montelukast+Levocetirizine | Respiratory |

**Guideline sources:** ESC/EAS, ACC/AHA, ADA 2024, GINA 2024, COGENT trial, UKPDS, ONTARGET, SABINA studies

---

### 3. `interactions.json` (8.4 KB)

**Purpose:** Pre-built cross-category drug conflict scenarios for the interaction checker feature.

**Structure:**
- `scenarios[]` — 6 detailed interaction scenarios with severity, mechanism, recommendation, safer alternative
- `interaction_pairs{}` — flat lookup map (14 entries) mapping `"drug_a+drug_b"` → scenario ID
- `additional_flags{}` — extra warnings (aspirin+ibuprofen)

**Scenarios:**
| # | Pattern | Severity | Key Risk |
|---|---------|----------|----------|
| 1 | Metformin + NSAIDs | High | Renal impairment → lactic acidosis |
| 2 | Clopidogrel + Omeprazole | High | CYP2C19 inhibition → loss of antiplatelet effect |
| 3 | ARBs + NSAIDs | Moderate | Combined renal arteriole constriction → AKI |
| 4 | Metformin + IV Contrast | High | Contrast nephrotoxicity → metformin accumulation |
| 5 | Atorvastatin + Azithromycin | Moderate | QT prolongation (primarily from azithromycin) |
| 6 | Salbutamol + Cardiac drugs | Moderate | Tachycardia + hypokalemia in CAD/HF patients |

**How lookup works:** Backend receives two drug IDs → concatenates as `"drug_a+drug_b"` → checks `interaction_pairs` map → returns matching scenario.

---

### 4. `reimbursement.json` (10.1 KB)

**Purpose:** Insurance/scheme coverage rules per drug category for the reimbursement guidance feature.

**Structure:**
- `schemes{}` — 5 scheme definitions (PM-JAY, CGHS, ESIC, Jan Aushadhi, Private Insurance) with coverage models and key rules
- `drug_coverage{}` — 6 drug-category buckets, each with per-scheme status text (now includes specific per-drug ESIC availability) and `agent_questions[]` the chatbot should ask

**Schemes covered:**
| Scheme | Type | Drug Coverage Model |
|--------|------|-------------------|
| PM-JAY | Govt insurance | Package-based (drugs bundled in hospital tariff) |
| CGHS | Employer scheme | Formulary-based (free at wellness centres) |
| ESIC | Social insurance | Dispensary schedule (per-drug verified status) |
| Jan Aushadhi | Govt pharmacy | Cash purchase at 50-90% discount |
| Private | IRDAI-regulated | Inpatient only (OPD drugs rarely covered) |

**Sources:** CGHS MSO Formulary 2014, VMS Formulary 2023, ESIC drug schedule PDF, PM-JAY HBP 2.0, Jan Aushadhi product lists

---

### 5. `jan_aushadhi_prices.csv` (6.9 KB)

**Purpose:** Complete generic drug price list from Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP).

**Format:** Standard CSV with columns for drug name, variant/formulation, pack size, and MRP.

**Stats:** 94 rows covering all 6 drug categories (multiple strengths/formulations per drug)

**Usage:** Loaded into ChromaDB `pricing` collection. When user asks about drug cost, the system retrieves the Jan Aushadhi price and compares against brand MRP from `drugs_master.json` to show potential savings.

---

## Cross-JSON Data Model

> **Invariant:** Every production drug MUST appear in `drugs_master.json` and `reimbursement.json`.
> It MAY or MAY NOT appear in `comparisons.json` or `interactions.json` depending on whether we've curated those views.

| File | Scope | Drug count |
|------|-------|------------|
| `drugs_master.json` | Canonical list — the full drug universe | 31 (all) |
| `reimbursement.json` | Coverage rules for all master drugs, by category | 31 (all) |
| `comparisons.json` | Subset with hand-authored comparison tables | 23 of 31 |
| `interactions.json` | Subset with curated interaction scenarios | 13 of 31 |
| `jan_aushadhi_prices.csv` | Price list (multiple rows per drug) | 94 rows |

Drugs like ciprofloxacin or doxycycline are fully present in master + reimbursement but have no comparison table or interaction scenario — this is intentional, not a bug. The `has_manual_comparisons` and `has_manual_interactions` boolean flags on each drug in `drugs_master.json` make this explicit.

When the backend queries ChromaDB for a drug without curated tables, it returns the master record + Jan Aushadhi price + reimbursement text. The LLM (Gemini) + OpenFDA API fill the gap at runtime.

---

## Data Quality Notes

1. **MRP prices** are approximate retail ranges from major Indian online pharmacies (PharmEasy, Apollo, 1mg, Medkart). They are not NPPA ceiling prices. MRPs change with company revisions.
2. **CGHS codes** are verified against MSO 2014 and VMS 2023 official PDFs. Drugs without individual CGHS codes are covered under their therapeutic category bucket.
3. **ESIC status** is verified against the ESIC dispensary drug schedule PDF. `fdc_only` means the standalone molecule isn't listed but fixed-dose combinations containing it are. `kit_only` means only in pre-packed kits.
4. **PM-JAY** does not have a drug formulary — medicines are bundled within hospital package rates. The PM-JAY column reflects standard-of-care usage within packages, not a formal drug list.
5. **Comparison tables** are aligned with current international guidelines (GINA 2024, ADA 2024, ESC/EAS, ACC/AHA) but local hospital protocols may differ.
6. **Interaction scenarios** cover the most common cross-category conflicts relevant to our 6 drug categories. They are pre-built (not dynamically generated) and serve as the primary safety feature. OpenFDA label data supplements these for live queries.

## How This Data Flows

```
data/*.json → data_loader.py → ChromaDB collections
                                      ↓
User query → rag_engine.py → ChromaDB similarity search + OpenFDA API
                                      ↓
                              Gemini LLM (context + query → response)
```
