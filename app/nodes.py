import os
from typing import Literal
from pydantic import BaseModel, Field
from atlassian import Jira
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- HELPER: Initialize LLM ---
def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )

# --- HELPER: Cost Calculator ---
def calculate_llm_cost(response):
    """Calculates cost based on GPT-4o-mini rates."""
    input_price = 0.15 / 1_000_000
    output_price = 0.60 / 1_000_000
    
    usage = getattr(response, 'usage_metadata', {})
    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)
    
    return (prompt_tokens * input_price) + (completion_tokens * output_price)

# --- STRUCTURED DATA ---
class AuditResult(BaseModel):
    is_safe: bool = Field(description="Is the technical advice logical and safe?")
    reason: str = Field(description="If unsafe, explain why.")

# --- NODE 1: Primary Agent ---
def primary_agent_node(state):
    print("🤖 Primary Agent: Thinking...")
    llm = get_llm()
    response = llm.invoke(state["messages"])
    cost = calculate_llm_cost(response)
    
    return {
        "messages": [response],
        "total_cost": state.get("total_cost", 0.0) + cost
    }

# --- NODE 2: Logic Auditor ---
def auditor_node(state):
    print("⚖️ Auditor: Reviewing response...")
    last_message = state["messages"][-1].content
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(AuditResult)
    
    audit_prompt = f"""
    You are a Senior SRE Auditor. 
    INVENTORY: Known Servers are [Production-DB-1, Production-Web-1]. 
    X-7-Alpha is NON-EXISTENT.
    
    REVIEW: "{last_message}"
    
    RULES: 
    1. If the agent gives commands for X-7-Alpha, is_safe = False.
    2. The agent must explicitly state X-7-Alpha does not exist to be safe.
    """
    
    result = structured_llm.invoke(audit_prompt)
    audit_cost = 0.00005 # Estimate for structured output tokens
    
    return {
        "is_safe": result.is_safe,
        "audit_report": result.reason,
        "total_cost": state.get("total_cost", 0.0) + audit_cost
    }

# --- NODE 3: Jira Incident Handler ---
def jira_node(state):
    current_bill = state.get("total_cost", 0.0)
    print(f"🚨 Jira Node: Logging incident. Current Session Cost: ${current_bill:.5f}")
    
    jira = Jira(
        url=os.getenv("JIRA_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("JIRA_API_TOKEN"),
        cloud=True
    )
    
    report = state.get("audit_report", "Unknown logic failure.")
    
    description = (
        f"Auditor Report: {report}\n\n"
        f"--- METRICS ---\n"
        f"Total API Cost for Resolution: ${current_bill:.5f}"
    )
    
    issue = jira.issue_create(fields={
        'project': {'key': os.getenv("JIRA_PROJECT_KEY")},
        'summary': "SENTINEL: AI Hallucination Flagged",
        'description': description,
        'issuetype': {'name': 'Report an incident'}
    })
    
    print(f"🎫 Incident Logged: {issue['key']}")
    
    feedback = (
        f"CRITICAL: Flagged in {issue['key']}. REASON: {report}. "
        "INSTRUCTION: Explicitly state X-7-Alpha does not exist."
    )
    
    return {"messages": [("system", feedback)]}

# --- NODE 4: Efficiency Report (ROI) ---
def efficiency_report_node(state):
    print("📊 Generating Efficiency Report...")
    
    # SRE Cost Benchmarks
    HUMAN_HOURLY_RATE = 85.00
    HUMAN_TIME_MINUTES = 10.0
    HUMAN_COST_ESTIMATE = (HUMAN_HOURLY_RATE / 60) * HUMAN_TIME_MINUTES
    
    ai_total_cost = state.get("total_cost", 0.0)
    savings = HUMAN_COST_ESTIMATE - ai_total_cost
    roi_multiple = HUMAN_COST_ESTIMATE / ai_total_cost if ai_total_cost > 0 else 0
    
    report = (
        f"\n" + "-"*30 +
        f"\n📈 SENTINEL ROI REPORT"
        f"\nEstimated Human Cost: ${HUMAN_COST_ESTIMATE:.2f} (10m @ $85/hr)"
        f"\nActual AI Cost:        ${ai_total_cost:.5f}"
        f"\nTotal Savings:        ${savings:.2f}"
        f"\nEfficiency Boost:     {roi_multiple:.1f}x Cheaper" +
        f"\n" + "-"*30
    )
    
    print(report)
    return {"audit_report": report}