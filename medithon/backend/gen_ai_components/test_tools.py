from tool_trial import execute_tool

print("\n--- Drug Info Test ---")
res = execute_tool("drug_information_retrieval", {"drug_name": "paracetamol"})
print(res)

print("\n--- Interaction Test ---")
res = execute_tool("drug_interaction_checker", {"drug_list": ["metformin", "ibuprofen"]})
print(res)

print("\n--- Reimbursement Test ---")
res = execute_tool("reimbursement_navigator", {"drug_name": "paracetamol"})
print(res)

print("\n--- Comparison Test ---")
res = execute_tool("comparative_analysis", {"drug_names": ["paracetamol", "ibuprofen"]})
print(res)
