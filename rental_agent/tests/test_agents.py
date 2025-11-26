import asyncio
from unittest.mock import patch

import pytest
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

from agents import leasing_orchestrator


@pytest.fixture
def session_service():
    """Provides an in-memory session service. for isolated tests."""
    return InMemorySessionService()

@pytest.fixture
def runner(session_service):
    """Provides an initialized Runner instance for the orchestrator agent."""
    return Runner(
        agent=leasing_orchestrator,
        app_name="RentAgent_App_Test",
        session_manager=session_service
    )

@pytest.fixture
async def setup_session(runner):
    """Provides an initialized Runner instance for the orchestrator agent."""
    return Runner(
        agent=leasing_orchestrator,
        app_name="RentAgent_App_Test",
        session_manager=session_service
    )

@pytest.fixture
async def setup_session(runner):
    """Creates a new session for a test user."""
    USER_ID = "test_applicant_101"
    session = await runner.session_manager.create_session(user_id=USER_ID, app_name="RentAgent_App_Test")
    return USER_ID, session.id

def mock_check_credit_score(application_data: dict) -> dict:
    """MOCK that returns a controlled, high credit score."""
    return {"credit_score": 750, "financial_notes": "Excellent credit history."}

def mock_validate_docuemtns(document_list: list) -> dict:
    """MOCK that returns high docuemtn integrity and no fraud."""
    return {"doc_integrity_score" : 0.99, "is_fraudulent" :  False}

@pytest.mark.asyncio
async def test_successful_application_flow(runner, setup_session):
    """
    Tests the complete end-to-end flow, ensuring the agent move from Inquiry to Screening and reders an approval decision. Mocks external tool calls to ensure predicatable results.
    """

    user_id,session_id =setup_session

    with patch('agents.tools.check_credit_score', side_effect=mock_check_credit_score), \
         patch('agents.tools.validate_docuemtns', side_effect=mock_validate_docuemtns):

        result_1 = await asyncio.to_thread(
            lambda:runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=runner.agent.get_content_class()(parts=[runner.agent.get_part_class()(text="I want to apply")])
            )
        )

        assert "name" in result_1.events[-1].message.tedxt.lower() or "income" in result_1.events[-1].message.tedxt.lower()

        result_2 = await asyncio.to_thread(
            lambda:runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=runner.agent.get_content_class()(parts=[runner.agent.get_part_class()(text="My name is Jane Doe.")])
            )
        )
        assert result_2.events[-1].message.text != "Application data collection complete. Proceeding to Screening Pipeline."