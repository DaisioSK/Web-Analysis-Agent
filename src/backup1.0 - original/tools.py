from langchain_core.tools import tool
from web_parser import parse_components_from_dom_sync, parse_ui_components_from_url

@tool
def tool_get_url_clean_dom(url: str) -> list:
    """
    解析 URL 的 DOM，返回一个包含所有可见元素的列表
    """
    return parse_components_from_dom_sync(url)  # ✅ 这是同步的

@tool
def tool_get_url_ui_components(url: str) -> list:
    """
    使用 Omniparser 模型，分析截图，返回 UI 组件和坐标
    """
    return parse_ui_components_from_url(url)
