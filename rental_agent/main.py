import asyncio
from typing import Optional

from google.adk import Runner
from google.adk.sessions import InMemorySessionService, Session

from agents.orchestrator import leasing_orchestrator

if __name__ == "__main__":
    session_service = InMemorySessionService()

    runner = Runner(
        agent=leasing_orchestrator,
        app_name="RentAgent_App",
        session_service=session_service
    )

    USER_ID = "applicant_123"

    async def run_application_query(message: str, session_id: Optional[str] = None) -> str:
        """
        Sends a message to the agent and streams the response events.
        Uses asyncio.to_thread to run the synchronous runner.run() method.

        CRITICAL FIX: Dynamically loads Content and Part classes because static imports fail.
        """

        try:
            ad_types = __import__('google.adk.messages', fromlist = ['Content', 'Parts'])
            Content_cls, Part_cls = ad_types.Content, ad_types.Part

        except ImportError:
            raise RuntimeError("ADK Import Error: Cannot find Cotnent/Part classes via dynamic loading. "
                               "Check ADK installation or version compatibility.")

        if not session_id:
            session: Session = await runner.session_service.create_session(
                user_id=USER_ID,
                app_name="RentAgent_App",
            )
            session_id =session_id
            print(f"--- New Session Created: {session_id} ---")

        print (f"\nUSER: {message}")

        final_response_text = ""
        new_context_message_dict = {
            "parts":[{"text":message}]
        }

        new_content_message = Content_cls(
            parts=[Part_cls(text=message)]
        )
        result = await asyncio.to_thread(
            lambda: runner.run(
                user_id=USER_ID,
                session_id=session_id,
                new_message=new_content_message,
            )
        )

        for event in result.events:
            if event.is_final_response():
                final_response_text = event.message.text
                print(f"AGENT RESPONSE: {final_response_text}")
        return session_id

    async def main_application_flow():
        print("--- Strating Leasing Application Flow Simulation ---")

        s_id = await run_application_query("I'd like to apply for the apartment on 123 Main St. My name is Alex.")

        s_id = await run_application_query("My monthly income is $5000." , s_id)

        await run_application_query("I agree to the credit check.", s_id)

        print("\n--- Flow Complete. The orchestrator should have rendered a final decision ---")

    asyncio.run(main_application_flow())