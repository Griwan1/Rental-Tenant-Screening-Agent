from google.adk.agents import LlmAgent
from .sub_agents import MODEL_NAME, inquiry_agent,screening_pipeline

# Root Agent (entry point with full MAS hierarchy).
leasing_orchestrator= LlmAgent(
    model=MODEL_NAME,
    name="Leasing_Orchestrator_Agent",
    description="The main agent for tenant application processing. Manages the full lifecycle from inquiry to final decision.",
    instruction=(
        "You are the Leasing Orchestrator. Your role is to guide the user through the application process."
        "First, delegate to the Inquiry_Agent to collect all data."
        "Once complete, delegate tot he Screening_Pipeline to process the application."
        "Your final output is the decision from the Decision_Agent."
    ),
    sub_agents=[
        inquiry_agent,
        screening_pipeline
    ]
)