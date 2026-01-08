from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages

class SentinelState(TypedDict):
    # Tracks the history of the conversation
    messages: Annotated[list, add_messages]
    
    # SYSTEM TELEMETRY
    health_status: str  # "HEALTHY", "DEGRADED", "FAILED"
    current_model: str  # e.g., "gpt-4o"
    failure_type: Optional[str] # "HALLUCINATION", "DOWNTIME", "DRIFT"
    retry_count: int
    
    # BUSINESS CONTEXT
    jira_ticket_key: Optional[str]