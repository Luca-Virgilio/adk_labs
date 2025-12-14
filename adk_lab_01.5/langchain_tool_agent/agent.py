import os
import sys
sys.path.append("..")

from google.adk import Agent
from google.adk.tools.langchain_tool import LangchainTool # import
from google.adk.agents.callback_context import CallbackContext

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv

load_dotenv()

root_agent = Agent(
    name="lanchgain_tool_agent",
    model=os.getenv("MODEL"),
    description="Answers questions using Wikipedia.",
    instruction="""Research the topic suggested by the user.
    Share the information you have found with the user.""",
    # Add the LangChain Wikipedia tool below
        tools = [
        # Use the LangchainTool wrapper...
        LangchainTool(
            # to pass in a LangChain tool.
            # In this case, the WikipediaQueryRun tool,
            # which requires the WikipediaAPIWrapper as
            # part of the tool.
            tool=WikipediaQueryRun(
              api_wrapper=WikipediaAPIWrapper()
            )
        )
    ]

)