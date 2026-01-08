from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Union
import operator

# Import the nodes from app/nodes.py
from app.nodes import (
    primary_agent_node, 
    auditor_node, 
    jira_node, 
    efficiency_report_node
)

# 1. Define the State (The system's memory)
class SentinelState(TypedDict):
    # operator.add allows messages to accumulate instead of overwriting
    messages: Annotated[List, operator.add]
    is_safe: bool
    audit_report: str
    retry_count: int
    total_cost: float # Tracks the cumulative API spend

# 2. Initialize the Graph
workflow = StateGraph(SentinelState)

# 3. Add Nodes (The Workers)
workflow.add_node("primary_agent", primary_agent_node)
workflow.add_node("auditor", auditor_node)
workflow.add_node("jira_incident_handler", jira_node)
workflow.add_node("efficiency_report", efficiency_report_node)

# 4. Set the Entry Point
workflow.set_entry_point("primary_agent")

# --- THE LOGIC FLOW ---

# Rule: Every AI response must be audited
workflow.add_edge("primary_agent", "auditor")

# The Router: Decision engine after audit
def route_after_audit(state: SentinelState):
    if state.get("is_safe") is True:
        print("🟢 Graph: Response Verified. Generating ROI Report.")
        return "generate_report"
    else:
        print("🔴 Graph: Audit Failed. Routing to Jira for Remediation.")
        return "trigger_jira"



# Defining the Conditional Fork
workflow.add_conditional_edges(
    "auditor",
    route_after_audit,
    {
        "generate_report": "efficiency_report",
        "trigger_jira": "jira_incident_handler"
    }
)

# Loop back: After Jira logs and provides feedback, let the Agent try again
workflow.add_edge("jira_incident_handler", "primary_agent")

# Final Edge: End the session after the report is printed
workflow.add_edge("efficiency_report", END)

# 5. Compile the Graph
app = workflow.compile()