from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_community.tools import TavilySearchResults
from datetime import datetime

PROMPT = f"""
You are an expert researcher.
Be persistent when gathering information and exact when answering questions rather than speculative.
Try to gather information piece by piece rather than trying to fetch it all at once.
If you are not completely sure about the full accuracy of an answer, keep attempting to gather more information rather than making assumptions or guessing.

The current date is {datetime.utcnow()}.
"""

def test_trajectory_cycles():
    model = init_chat_model("ollama:deepseek-r1")
    model.bind_tools([TavilySearchResults(max_results=5)])
    tools = [TavilySearchResults(max_results=5)]
    agent = create_react_agent(
        model,
        tools,
        prompt=PROMPT
    )
    res = agent.invoke({
        "messages": [
            HumanMessage(
                content="What is the current US position on crypto and how does it relate to LangChain?"
            )
        ]
    })
    print(res["messages"][-1].content)
