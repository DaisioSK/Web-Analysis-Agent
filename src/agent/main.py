import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI
# from agent.agent_tools import get_mcp_tools
from agent_tools import get_mcp_tools
from pydantic import BaseModel
from typing import List
from langchain.output_parsers import PydanticOutputParser


class Component(BaseModel):
    name: str
    bbox: List[float]  # 比如 [x1, y1, x2, y2]
    interactivity: bool
    sno: int
    tracking_method: str
    metric_definition: str


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

parser = PydanticOutputParser(pydantic_object=Component)

format_instructions = parser.get_format_instructions()
escaped_instructions = format_instructions.replace("{", "{{").replace("}", "}}")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are an intelligent web analysis assistant that selects and uses tools to analyze web pages. 
        You can use extract image tool to extract the image from the URL, then get the bbox of the image and other information.
        You can use rag tool to get enriched context for the user's query. 
        Pleaes Return the Component object in JSON. {escaped_instructions}"""),
    MessagesPlaceholder("chat_history"),
    ("user", "Analyze the URL below and suggest what should be tracked. URL: {url}"),
    MessagesPlaceholder("agent_scratchpad"),
])

tools = get_mcp_tools()

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=ConversationSummaryBufferMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True
    ),
    verbose=True,
    max_iterations=6,
    return_intermediate_steps=True
)

if __name__ == "__main__":
    out = executor.invoke({"url": "www.google.com"})
    print("\n--- Agent Output ---")
    print(out["output"])
