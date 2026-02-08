import os
import json
from typing import List, Dict, Any
from openai import OpenAI

# -----------------------------------------------------------------------------
# IMPORTS (Ensure you have these files or replace with your actual values)
# -----------------------------------------------------------------------------
try:
    from config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, OPENAI_MODEL, OPENAI_API_KEY
    from tools import execute_tool
    from guardrails import GuardrailsFramework
except ImportError:
    # FALLBACKS FOR TESTING (If you don't have the files yet)
    print("⚠️ Warning: specific modules not found. Using fallback configuration.")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # Ensure this is set!
    OPENAI_MODEL = "gpt-4-turbo"
    SYSTEM_PROMPT = "You are a Medical Representative AI. Use tools to answer questions."
    USER_PROMPT_TEMPLATE = "{query}"
    
    # Dummy Tool Executor
    def execute_tool(name, args):
        return f"[Mock Output] Executed {name} with {args}"

    # Dummy Guardrails
    class GuardrailsFramework:
        def __init__(self, audit_logfile): pass
        def validate_input(self, msg): return {"status": "allowed"}
        def validate_output(self, msg, ans, tools): return {"status": "allowed", "safe_response": ans}
        def audit(self, msg, tools, ans): pass

# -----------------------------------------------------------------------------
# SETUP CLIENT & GUARDRAILS
# -----------------------------------------------------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
guardrails = GuardrailsFramework(audit_logfile="audit_log.jsonl")

# -----------------------------------------------------------------------------
# TOOL SCHEMA (OpenAI Format)
# -----------------------------------------------------------------------------
TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "drug_information_retrieval",
            "description": "Retrieve drug information (MoA, dosing, safety, indications).",
            "parameters": {
                "type": "object",
                "properties": {"drug_name": {"type": "string"}},
                "required": ["drug_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comparative_analysis",
            "description": "Retrieve comparison data between multiple drugs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_names": {"type": "array", "items": {"type": "string"}, "minItems": 2}
                },
                "required": ["drug_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drug_interaction_checker",
            "description": "Retrieve drug-drug interaction information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_list": {"type": "array", "items": {"type": "string"}, "minItems": 2}
                },
                "required": ["drug_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reimbursement_navigator",
            "description": "Retrieve reimbursement, insurance coverage, and formulary details.",
            "parameters": {
                "type": "object",
                "properties": {"drug_name": {"type": "string"}},
                "required": ["drug_name"]
            }
        }
    }
]

# =============================================================================
# Medical Representative Agent Class
# =============================================================================

class MedicalRepAgent:
    """
    AI Agent for Medical Representative Queries
    """
    def __init__(self):
        self.model = OPENAI_MODEL
        self.max_tool_iterations = 5

    def _build_messages(self, history: List[Dict], current_message: str) -> List[Dict]:
        """Converts frontend history into OpenAI message format."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in history:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        user_prompt = USER_PROMPT_TEMPLATE.format(query=current_message)
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def process_message(self, message: str, history: List[Dict]) -> str:
        """Main entrypoint: processes user message with history."""
        
        # 1. Input Guardrails
        input_check = guardrails.validate_input(message)
        if input_check["status"] != "allowed":
            return input_check["message"]

        messages = self._build_messages(history, message)
        tool_calls_log = []
        tool_outputs = []
        iteration = 0

        # 2. Tool Calling Loop
        while iteration < self.max_tool_iterations:
            iteration += 1

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_OPENAI,
                tool_choice="auto"
            )

            assistant_msg = response.choices[0].message

            # If no tools called, we have the final answer
            if not assistant_msg.tool_calls:
                draft_answer = assistant_msg.content

                # Output Guardrails
                output_check = guardrails.validate_output(message, draft_answer, tool_outputs)
                final_answer = output_check["message"] if output_check["status"] != "allowed" else output_check["safe_response"]

                # Audit Log
                guardrails.audit(message, tool_calls_log, final_answer)
                return final_answer

            # Add assistant's "tool call" request to history
            messages.append(assistant_msg)

            # Execute Tools
            for tool_call in assistant_msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_calls_log.append({"tool_name": tool_name, "tool_args": tool_args})
                
                # Execute logic
                tool_result = execute_tool(tool_name, tool_args)
                tool_outputs.append(tool_result)

                # Feed result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        return "⚠️ Tool execution loop exceeded. Please rephrase."

    def get_welcome_message(self) -> str:
        return (
            "Namaste! 🙏 I'm **MedBuddy**, your Medical Representative AI.\n"
            "Type 'New Patient' to start fresh or 'End Chat' to stop."
        )

# =============================================================================
# MAIN EXECUTION LOOP (With Memory Reset Logic)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Starting Medical Representative Agent")
    print("=" * 60)

    agent = MedicalRepAgent()
    print(f"\n🤖 Agent: {agent.get_welcome_message()}")

    # This list holds the conversation history (The Memory)
    history = []

    while True:
        try:
            user_input = input("\n👨‍⚕️ Doctor: ").strip()

            # --- TRIGGER 1: EXIT ---
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break

            # --- TRIGGER 2: END CHAT (Clear Memory) ---
            if "end chat" in user_input.lower() or "stop session" in user_input.lower():
                history.clear()
                print("\n" + "-"*50)
                print("🛑 [System] Chat Ended. Memory Wiped.")
                print("-" * 50)
                print(f"\n🤖 Agent: {agent.get_welcome_message()}")
                continue # Skip processing

            # --- TRIGGER 3: NEW PATIENT (Reset Memory) ---
            # We clear history, but we proceed to process this message as the start of new chat.
            if "new patient" in user_input.lower() or "start over" in user_input.lower():
                history.clear()
                print("\n" + "-"*50)
                print("🔄 [System] Memory Cleared: Starting New Patient Session")
                print("-" * 50)

            # --- PROCESS MESSAGE ---
            print("🤖 Thinking...")
            response = agent.process_message(user_input, history)
            
            print(f"\n📄 Response: {response}")

            # Update Memory
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")