import os
import json
from typing import List, Dict, Any

from openai import OpenAI

from config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, OPENAI_MODEL, OPENAI_API_KEY
from tools import execute_tool
from guardrails import GuardrailsFramework


# -------------------------------
# OpenAI Client Setup
# -------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# Guardrails
guardrails = GuardrailsFramework(audit_logfile="audit_log.jsonl")


# -------------------------------
# Tool Schema (OpenAI Format)
# -------------------------------
TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "drug_information_retrieval",
            "description": "Retrieve drug information (MoA, dosing, safety, indications) using vector database search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"}
                },
                "required": ["drug_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comparative_analysis",
            "description": "Retrieve comparison data between multiple drugs using vector database search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2
                    }
                },
                "required": ["drug_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drug_interaction_checker",
            "description": "Retrieve drug-drug interaction information using vector database search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2
                    }
                },
                "required": ["drug_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reimbursement_navigator",
            "description": "Retrieve reimbursement, insurance coverage, and formulary details using vector database search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"}
                },
                "required": ["drug_name"]
            }
        }
    }
]


# =============================================================================
# Medical Representative Agent
# =============================================================================

class MedicalRepAgent:
    """
    AI Agent for Medical Representative Queries

    This agent:
    - Accepts a message and history (like Gemini InsuranceAgent)
    - Uses OpenAI tool calling
    - Calls vector database tools
    - Applies input/output guardrails
    - Logs audit trail
    """

    def __init__(self):
        self.model = OPENAI_MODEL
        self.max_tool_iterations = 5

    def _build_messages(self, history: List[Dict], current_message: str) -> List[Dict]:
        """
        Converts frontend history into OpenAI message format.
        """

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add history
        for msg in history:
            if msg["role"] not in ["user", "assistant"]:
                continue

            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user query
        user_prompt = USER_PROMPT_TEMPLATE.format(query=current_message)
        messages.append({"role": "user", "content": user_prompt})

        return messages

    def process_message(self, message: str, history: List[Dict]) -> str:
        """
        Main entrypoint: processes user message with history.

        Args:
            message: current user query
            history: list of dicts [{"role": "user", "content": ...}, {"role":"assistant", ...}]

        Returns:
            agent response text
        """

        # ---------------------------
        # Input Guardrails
        # ---------------------------
        input_check = guardrails.validate_input(message)
        if input_check["status"] != "allowed":
            return input_check["message"]

        # Build OpenAI formatted messages
        messages = self._build_messages(history, message)

        tool_calls_log = []
        tool_outputs = []

        # ---------------------------
        # Tool Calling Loop
        # ---------------------------
        iteration = 0

        while iteration < self.max_tool_iterations:
            iteration += 1

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_OPENAI,
                tool_choice="auto"
            )

            assistant_msg = response.choices[0].message

            # If no tools called, final answer is generated
            if not assistant_msg.tool_calls:
                draft_answer = assistant_msg.content

                # Output guardrails
                output_check = guardrails.validate_output(message, draft_answer, tool_outputs)

                if output_check["status"] != "allowed":
                    final_answer = output_check["message"]
                else:
                    final_answer = output_check["safe_response"]

                # Audit
                guardrails.audit(message, tool_calls_log, final_answer)

                return final_answer

            # Add assistant tool-call message to history
            messages.append({
                "role": "assistant",
                "tool_calls": assistant_msg.tool_calls
            })

            # Execute each tool
            for tool_call in assistant_msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_calls_log.append({
                    "tool_name": tool_name,
                    "tool_args": tool_args
                })

                tool_result = execute_tool(tool_name, tool_args)
                tool_outputs.append(tool_result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        # If loop ends without final answer
        return (
            "⚠️ Tool execution loop exceeded maximum iterations. "
            "Please rephrase the query or specify drug names clearly."
        )

    def get_welcome_message(self) -> str:
        return (
            "Namaste! 🙏 I'm **MedBuddy**, your Medical Representative AI.\n\n"
            "I can help with:\n"
            "• Drug mechanism of action (MoA)\n"
            "• Indications and safety profile\n"
            "• Drug-drug interactions\n"
            "• Reimbursement and coverage details\n"
            "• Drug comparisons\n\n"
            "What drug information do you need today?"
        )


# =============================================================================
# Synchronous Wrapper (like your InsuranceAgent)
# =============================================================================

def process_message_sync(agent: MedicalRepAgent, message: str, history: List[Dict]) -> str:
    return agent.process_message(message, history)


# =============================================================================
# Testing in CLI
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Medical Representative Agent (OpenAI + Chroma + Guardrails)")
    print("=" * 60)

    agent = MedicalRepAgent()
    print(agent.get_welcome_message())

    history = []

    while True:
        msg = input("\nDoctor Query > ")

        if msg.lower() in ["exit", "quit"]:
            print("\nExiting agent...")
            break

        response = process_message_sync(agent, msg, history)

        print("\nAGENT RESPONSE:\n")
        print(response)

        # Update history like Gemini style
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response})
