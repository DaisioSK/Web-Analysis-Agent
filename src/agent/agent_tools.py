from langchain.tools import tool
import requests

TOOL_LIST_API = "http://localhost:8000/tool/list"
TOOL_CALL_MAP = {
    "parse_dom": "http://localhost:8000/tool/parse_dom",
    "analyze_screenshot": "http://localhost:8000/tool/analyze_screenshot"
}

from langchain.tools import Tool

def get_mcp_tools():
    TOOL_CALL_PREFIX = "http://localhost:8000/tool/"
    resp = requests.get("http://localhost:8000/tool/list")
    tools = []

    for tool_meta in resp.json().get("tools", []):
        name = tool_meta["name"]
        description = tool_meta["description"]
        endpoint = TOOL_CALL_PREFIX + name  # 自动拼接 URL

        def dynamic_tool(url: str, name=name, endpoint=endpoint):
            if name == "query_rag":
                # 特殊处理 query_rag 工具
                response = requests.post(endpoint, json={"query": url})
            else:
                response = requests.post(endpoint, json={"url": url})
            return response.json()

        tools.append(
            Tool(
                name=name,
                description=description,
                func=dynamic_tool,
            )
        )
    return tools

