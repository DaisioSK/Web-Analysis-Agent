from fastapi import APIRouter
from pydantic import BaseModel
from mcp_server.utils.web_parse_utils import parse_components_from_dom_sync  # 复用你已有的逻辑

router = APIRouter()

MCP_TOOL_META = {
    "name": "parse_dom",
    "description": "提取网页中可追踪组件，如按钮、输入框、表单等"
}


class URLInput(BaseModel):
    url: str

@router.post("/parse_dom")
def parse_dom_tool(input: URLInput):
    """
    extract components from the DOM of a webpage, such as buttons, input fields, forms, etc.
    """
    result = parse_components_from_dom_sync(input.url)
    return {"components": result}
