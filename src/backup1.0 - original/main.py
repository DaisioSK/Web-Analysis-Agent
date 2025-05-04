from dotenv import load_dotenv
import os
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import tool_get_url_clean_dom, tool_get_url_ui_components
import nest_asyncio
from IPython.display import display, Markdown

import asyncio


# 获取 notebook 所在路径的上一级（即项目根目录）
BASE_DIR = Path.cwd().parent

# 加载 .env 文件
load_dotenv(dotenv_path=BASE_DIR / ".env")

openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

print(openai_api_key)

system_prompt = """
You are a very helpful assistant that helps user extract web tracking solution from a web page.
When you are asked to analyze a web page, please consider 
- use the Omniparser tool to parse the web page screenshot, and provide a list of components with their coordinates.
- use the image_captioning tool to generate captions for images in the web page.
- use the parse_components_from_dom tool to extract important html elements as trackable components in a web page.

the image captionings, image content and web page's DOM structure.
"""

user_prompt = """
I will give you URL below, please help me analyze the web page and provide a list of components that are worth tracking.
The components can be buttons, links, images, forms, etc.


Please help me analyze this screenshot of web page, and list down all the web components that worth tracking.
When you analyze the web page, please consider image captionings, image content and web page's DOM structure.
For each of the components you selected, tell me their names, coordinates and a description on how we can track it.

URL: {url}
"""

# passing the template to the LangChain model using tuple
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", user_prompt),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key=openai_api_key,
    openai_api_base = "https://api.openai.com/v1",
    temperature=0.0,
    # max_tokens=2048,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)



memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)


tools= [tool_get_url_clean_dom, tool_get_url_ui_components]

agent= create_tool_calling_agent(
    llm=llm, tools=tools, prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

async def main():
    out = await agent_executor.ainvoke({
        "url": "www.google.com",
    })
    display(Markdown(out["output"]))

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())