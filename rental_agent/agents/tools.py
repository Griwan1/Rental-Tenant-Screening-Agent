from typing import Dict, Any, List
import time

MODEL_NAME = 'gemini-2.5-flash'

def check_credit_score(applicant_data: Dict [str, Any]) -> Dict [str, Any]:
    """Retrieves and analyzes the applicant's credit and eviction history from an external credit bureau.

    :param applicant_data: Data provided by the calling agent (e.g., the application's name/ID).
    :return: Dictionary of financial findings.
    """
    print("-> TOOL: External Credit Bureau API is getting called !!!")
    time.sleep(1)
    score = 720 # Mock data
    notes = "On-time rent payments for the last 3 years."
    return {"credit_score": score, "financial_notes": notes}


def validate_documents(document_list: List[str]) -> Dict [str, Any]:
    """
    TOOL: Uses OCR and fraud detection to verify identity and income documents (e.g., ID and pay stubs).

    :param document_list: List of document identifiers (e.g., filename or URLs).
    :return: Dictionary of document containing the integrity and fraud status.
    """
    print("-> TOOL: (MCP Protocol) External Document Verification Service is getting called !!!")
    is_fraudulent = False
    integrity_score = 0.95
    return {"doc_integrity_score": integrity_score, "is_fraudulent": is_fraudulent}

def save_applicant_data(session_state: Any, data : Dict[str, Any]) -> str:
    """
    TOOL: Saves data collected by the LLM into the session state.
    The LLM should call this tool immediately after receiving data from the user.

    :param session_state: Current session object.
    :param data: A dictionary containing the key-value pairs fo applicant data to save (e.g., {'name': 'John Doe'}).
    :return: A confirmation message.
    """
    print(f"--- TOOL: Saving applicant data to session : {data}")
    for key, value in data.items():
        session_state.set(key,value)
    return "Data saved successfully. Ready for next step."