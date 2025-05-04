from fastapi import APIRouter
from pydantic import BaseModel
from mcp_server.utils.web_parse_utils import parse_ui_components_from_url  # 复用你已有的逻辑

router = APIRouter()

MCP_TOOL_META = {
    "name": "analyze_screenshot",
    "description": "对网页截图执行图像理解（如 OCR、布局分析、视觉组件识别）"
}

class URLInput(BaseModel):
    url: str

@router.post("/analyze_screenshot")
def analyze_screenshot_tool(input: URLInput):
    """
    对网页截图执行图像理解（如 OCR、布局分析、视觉组件识别）
    """
    result = parse_ui_components_from_url(input.url)
    return result