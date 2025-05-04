from pathlib import Path
from dotenv import load_dotenv
# load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")
load_dotenv()


from fastapi import FastAPI
from mcp_server.tools import dom_parser, screenshot_ocr, tool_registry, detect_language, extract_image, query_rag_tool


app = FastAPI(title="MCP Server", description="A local agent capability service platform")

# register the routers for the tool modules
app.include_router(dom_parser.router, prefix="/tool")
app.include_router(detect_language.router, prefix="/tool")
app.include_router(extract_image.router, prefix="/tool")
app.include_router(screenshot_ocr.router, prefix="/tool")
app.include_router(tool_registry.router, prefix="/tool")
app.include_router(query_rag_tool.router, prefix="/tool")



# 打开 cmd，然后进入项目目录
# cd "C:\Users\SichengLiu\Documents\SK MVP\langchain agent basic\langchain agent\src"
# conda activate ai_agent_env
# python -m uvicorn mcp_server.main:app
# 打开 http://localhost:8000/docs/