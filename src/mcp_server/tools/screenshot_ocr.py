from fastapi import APIRouter
from pydantic import BaseModel
from mcp_server.utils.web_parse_utils import parse_ui_components_from_url  # 复用你已有的逻辑

router = APIRouter()

MCP_TOOL_META = {
    "name": "analyze_screenshot",
    "description": "perform image understanding on webpage screenshots (e.g., OCR, layout analysis, visual component recognition)"
}

class URLInput(BaseModel):
    url: str

@router.post("/analyze_screenshot")
def analyze_screenshot_tool(input: URLInput):
    """
    perform image understanding on webpage screenshots (e.g., OCR, layout analysis, visual component recognition)
    """
    result = parse_ui_components_from_url(input.url)
    return result