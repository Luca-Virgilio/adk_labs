import asyncio
import os
from typing import Optional
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.llm_agent import Agent

# Attempt to load a local .env file (simple parser) so the script can be run
# from this folder without requiring external dotenv packages.
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r") as _f:
            for _ln in _f:
                _ln = _ln.strip()
                if not _ln or _ln.startswith("#"):
                    continue
                if "=" in _ln:
                    _k, _v = _ln.split("=", 1)
                    # Only set if not already present in environment
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        # Non-fatal: continue and rely on environment variables
        pass

def _init_adk_from_env() -> None:
    """Initializes google.adk either with API key (Google AI) or Vertex AI settings."""
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
    if use_vertex:
        project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GOOGLE_LOCATION") or "us-central1"
        if not project:
            raise RuntimeError(
                "Missing Google Cloud project. Set GOOGLE_CLOUD_PROJECT (or GOOGLE_PROJECT) and GOOGLE_CLOUD_LOCATION if needed."
            )
        # Initialize ADK for Vertex AI
        #adk.init(vertexai=True, project=project, location=location)
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GOOGLE_API_KEY environment variable. Set it in the environment or in the local .env file."
            )
        # Initialize ADK for Google AI API using the provided API key
        #adk.init(api_key=api_key)

# Initialize ADK before creating agents/runners
_init_adk_from_env()

# --- 1. Define Agent, App Name, and User Context ---

# Define the Agent. Since the query is general knowledge, we use a simple LLMAgent
# without any specific tools.
agent = Agent(
    model="gemini-2.5-flash",  # Use a suitable Gemini model
    name="CapitalFinderAgent",
    instruction="You are a helpful assistant that answers general knowledge questions concisely.",
    tools=[]  # No tools needed for this query
)

# Define context variables
APP_NAME = "app_agent"
USER_ID = "test_user_123"
SESSION_ID = "session_001"
QUERY = "What is the capital of France"

# --- 2. Setup Session Service and Runner ---

# Use InMemorySessionService for simulating session management in memory
session_service = InMemorySessionService()
print("✅ Created InMemorySessionService.")

# We'll create the session and runner inside an async main to await async APIs
async def main():
    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"✅ Created new session with ID: {session.id}")

    # Use Runner to orchestrate the agent execution loop in memory
    runner = Runner(
        agent=agent,           # The agent to run
        app_name=APP_NAME,     # Associates runs with our app
        session_service=session_service # Uses our session manager
    )
    print(f"✅ Created Runner for agent: {agent.name}")

    final_answer = await run_query_and_get_response(QUERY, runner, USER_ID, SESSION_ID)
    print("\n--- Final Agent Response ---")
    print(f"**Answer:** {final_answer}")
    print("----------------------------")

# --- 3. Define the Execution Function ---

async def run_query_and_get_response(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and returns the final response text."""
    print(f"\n>>> Running Query: **{query}**")
    
    # Prepare the user's message in the ADK Content format.
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "No response received."

    # run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # The is_final_response() flag marks the concluding message for the turn.
        if event.is_final_response():
            # Check if there is content and parts before accessing
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break  # Exit loop once the final response is found

    return final_response_text

# --- 4. Run the Script ---

# Run the async main to create session, runner, and execute the query
try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred during execution: {e}")