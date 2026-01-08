import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(role="PRIMARY"):
    """
    Directly routes to the best provider based on the agent's role.
    """
    if role == "PRIMARY":
        # Use direct OpenAI for maximum speed/reliability
        return ChatOpenAI(model=os.getenv("PRIMARY_MODEL"), temperature=0)
    
    if role == "RECOVERY":
        # Use direct Google for failover resilience
        return ChatGoogleGenerativeAI(model=os.getenv("RECOVERY_MODEL"))

    if role == "AUDITOR":
        # Use OpenRouter for the free Llama model (FinOps strategy)
        return ChatOpenAI(
            model=os.getenv("AUDITOR_MODEL"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1"
        )