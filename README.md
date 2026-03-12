# 🩺 MedRep AI (Project DMR)
**Your 24/7 Digital Medical Representative 🇮🇳**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](#)
[![LangChain](https://img.shields.io/badge/LangChain-Integration-green?logo=chainlink&logoColor=white)](#)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black?logo=openai&logoColor=white)](#)

A multimodal, RAG-based AI assistant for healthcare professionals that provides real-time, evidence-based drug information. It integrates pharmacology, interaction checking, and Indian reimbursement data (CGHS/Jan Aushadhi) using LangChain and Vector Databases to ensure safe, affordable, and accurate clinical decision-making.

## ⚠️ The Problem
Small-to-mid-size pharmaceutical firms face an existential challenge: traditional medical representatives cost $150k–$250k annually, yet struggle to deliver instant, accurate drug information to time-constrained physicians. 

Meanwhile, doctors suffer from **Cognitive Overload**:
* **Safety Blindspots:** Manual checks miss critical drug-drug interactions in polypharmacy cases during a 2-minute consult.
* **Financial Disconnect:** Inability to instantly verify reimbursement coverage (like CGHS) leads to prescription abandonment.
* **Tool Failure:** Existing solutions are either static databases lacking conversational AI or locked inside expensive EHR systems.

## 💡 The Solution
MedRep AI is a "Zero-Friction" clinical assistant. Instead of hunting through static PDFs, doctors can query our multi-vector RAG system using Text, Voice, or Vision to get instant, conflict-free medical intelligence.

### ✨ Key Features
* **🧠 Multi-Vector Parallel RAG:** Queries 4 distinct databases simultaneously (Pharmacology, Interactions, Reimbursement, Comparisons) for holistic answers.
* **🗣️ Voice & Vision Multimodality:** Doctors can dictate queries hands-free or upload photos of prescriptions for instant OCR and interaction checking.
* **🏥 Patient Session Memory:** Remembers patient context (e.g., "65 Male, Diabetic") throughout the consult to proactively flag contraindications. Triggered by commands like *"New Patient"*.
* **🛡️ Clinical Guardrails:** Enforces strict output parsing (Pydantic) to ensure answers are structured, evidence-based, and explicitly highlight critical warnings.
* **🇮🇳 Indian Context:** Built-in intelligence for Jan Aushadhi generic alternatives and CGHS pricing.

## 🏗️ Architecture & Tech Stack
* **LLM & Vision:** OpenAI `gpt-4o`
* **Embeddings:** OpenAI `text-embedding-3-small`
* **Framework:** LangChain (LCEL)
* **Vector Store:** ChromaDB (Local SQLite)
* **Frontend:** Streamlit
* **Audio Processing:** `SpeechRecognition`, `PyAudio`

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/medrep-ai.git](https://github.com/yourusername/medrep-ai.git)
cd medrep-ai
