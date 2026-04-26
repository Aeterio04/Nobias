"""
LangGraph Agent API Server

A simple loan approval agent built with LangGraph and served via FastAPI.
This demonstrates how to audit a production agent via API endpoint.

To run:
1. Install: pip install langgraph langchain langchain-groq fastapi uvicorn
2. Set GROQ_API_KEY in library/.env
3. Run: python examples/langgraph_agent_server.py
4. Server runs on http://localhost:8000
"""

import os
import sys
from pathlib import Path
from typing import TypedDict, Annotated
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "library" / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


# ══════════════════════════════════════════════════════════════════════════════
# LangGraph Agent Definition
# ══════════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """State for the loan approval agent."""
    input: str
    decision: str
    reasoning: str


def create_loan_agent():
    """Create a LangGraph loan approval agent."""
    
    # Initialize LLM
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")
    
    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.0,
    )
    
    # System prompt
    system_prompt = """You are a loan approval assistant.
Evaluate loan applications and respond with either APPROVE or DENY.
Be thorough in your evaluation.

Provide your decision in this format:
DECISION: [APPROVE or DENY]
REASONING: [Brief explanation]"""
    
    # Define agent node
    def evaluate_loan(state: AgentState) -> AgentState:
        """Evaluate the loan application."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["input"])
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse decision
        if "APPROVE" in response_text.upper():
            decision = "APPROVE"
        elif "DENY" in response_text.upper():
            decision = "DENY"
        else:
            decision = "UNCLEAR"
        
        return {
            "input": state["input"],
            "decision": decision,
            "reasoning": response_text,
        }
    
    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("evaluate", evaluate_loan)
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", END)
    
    return workflow.compile()


# ══════════════════════════════════════════════════════════════════════════════
# FastAPI Server
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(title="Loan Approval Agent API")

# Initialize agent
try:
    agent = create_loan_agent()
    print("✅ LangGraph agent initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    agent = None


class LoanRequest(BaseModel):
    """Request model for loan evaluation."""
    input: str


class LoanResponse(BaseModel):
    """Response model for loan evaluation."""
    decision: str
    reasoning: str


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Loan Approval Agent",
        "version": "1.0.0",
        "endpoints": {
            "evaluate": "/evaluate",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    """Health check with agent status."""
    return {
        "status": "healthy" if agent else "unhealthy",
        "agent_ready": agent is not None
    }


@app.post("/evaluate", response_model=LoanResponse)
def evaluate_loan(request: LoanRequest):
    """
    Evaluate a loan application.
    
    Args:
        request: LoanRequest with input text
    
    Returns:
        LoanResponse with decision and reasoning
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Run agent
        result = agent.invoke({"input": request.input})
        
        return LoanResponse(
            decision=result["decision"],
            reasoning=result["reasoning"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("LangGraph Loan Approval Agent Server")
    print("=" * 70)
    print("\nStarting server on http://localhost:8000")
    print("\nEndpoints:")
    print("  GET  /          - Service info")
    print("  GET  /health    - Health check")
    print("  POST /evaluate  - Evaluate loan application")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
