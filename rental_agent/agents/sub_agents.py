import time

from google.adk.agents import (ParallelAgent,
                               Agent,
                               SequentialAgent,
                               LlmAgent)
from google.adk.tools import FunctionTool
from typing import Dict, Any, List, Optional
from .tools import  validate_documents, check_credit_score,save_applicant_data

MODEL_NAME= 'gemini-2.5-flash'



# Mock Tools for Verification Agents
def validate_documents(session_state: Any) -> Dict[str, Any]:
    """MOCK TOOL: Simulates document authenticity check."""
    # mocking the result
    time.sleep(1)
    doc_score=95
    if session_state.get("income",0) < 5000:
        doc_score = 70

    return {
        "document_integrity_score": doc_score,
        "document_status": "Verified, but income check noted"
    }

def check_credit_score(session_state: Any) -> Dict[str, Any]:
    """MOCK TOOL: Simulates financial risk check."""
    time.sleep(1)
    credit_score=720
    if session_state.get("credit_consent") == "no":
        return {"error": "Credit check consent was denied."}

    return {
        "credit_score": credit_score,
        "eviction_history": "None",
        "financial_risk_level" : "Low"
    }

class InquiryLoopAgent(Agent):
    """
    Custom agent that implements the inquiry loop logic internally. It reporrtedly calls an inner LLM agent until required data is collected.
    """
    def __init__(self, name: str, max_loops: int = 5):
        super().__init__(name = name)
        self.max_loops = max_loops

        self.inquiry_llm_agent = LlmAgent(
            model= MODEL_NAME,
            name=f"{name}_Inquiry_LLM",
            instruction=(
                "You are the friendly Inquiry bot. Your goal is to collect all application data (name, income, credit_consent)"
                "Check the session state for missing fields. Only ask for ONE missing piece of data at a time."
                "If you receive a peice of data, use the `save_applicant_data` tool to store it immediately."
            ),
            tools=[FunctionTool(save_applicant_data)]
        )

    async def execute(self, session_state: Any, user_input : str) -> str:
        current_loop=0

        while current_loop < self.max_loops:
            # check for termination
            required_fields = ["name","income","credit_consent"]
            is_complete = all(session_state.get(field) is not None for field in required_fields)

            if is_complete:
                return "Application data collection complete. Proceeding to Screening Pipeline."

            response_text = await self.inquiry_llm_agent.execute(
                session_state,
                user_input
            )

            user_input =""
            current_loop += 1

            return response_text

        return "Application failed to complete within the maximum attempts. Please restart the process"

inquiry_agent =InquiryLoopAgent(name = "Inquiry_Agent", max_loops = 5)

doc_verification_agent = LlmAgent(
    model= MODEL_NAME,
    name="Doc_Verification_Agent",
    instruction="Verify provided application documents(ID, pay stubs) for authenticity and integrity. Use the validate_documents tool. Output the document integrity score.")

risk_analysis_agent =LlmAgent(
    model= MODEL_NAME,
    name="Risk_Analysis_Agent",
    instruction="Analyze the applicant's financial risk. Use the check_credit_score tool. Synthesize a brief report covering credit, eviction history and financial stability",
    tools=[FunctionTool(check_credit_score)]
)

compliance_agent = LlmAgent(
    model= MODEL_NAME,
    name="Compliance_Agent",
    instruction="AUDIT: Review the scores from Doc_Verification_Agent and Risk_Analysis_Agent comparing them against the strict Fair Housing Law criteria. Return 'COMPLIANT' or 'FAILURE' to the Orchestrator, with detailed reason"
)

decision_agent = LlmAgent(
    model= MODEL_NAME,
    name="Decision_Agent",
    instruction="FINALIZER: Based on the COMPLIANT state and the combined Risk Score, render a final decision (Approve, Conditional, Reject). Generate a concise, objective notification to the applicant."
)

parallel_verification_workflow = ParallelAgent(
    name="Parallel_Verification_Workflow",
    sub_agents=[doc_verification_agent,risk_analysis_agent]
)
screening_pipeline = SequentialAgent(
    name="Screening_Pipeline",
    sub_agents=[
        parallel_verification_workflow, # Step 1: Run parallel Checks
        compliance_agent,               # Step 2: Audit the results
        decision_agent                  # Step 3: Finalize the outcome
    ]
)