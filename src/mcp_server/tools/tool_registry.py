from fastapi import APIRouter
import importlib
import pkgutil
import mcp_server.tools as tools_pkg

router = APIRouter()

def discover_tool_modules():
    """动态发现所有 MCP 工具模块"""
    return [name for _, name, _ in pkgutil.iter_modules(tools_pkg.__path__)]

@router.get("/list")
def list_available_tools():
    """
    自动读取 MCP 工具模块中的 MCP_TOOL_META 字典
    """
    tools = []
    for mod_name in discover_tool_modules():
        try:
            mod = importlib.import_module(f"mcp_server.tools.{mod_name}")
            if hasattr(mod, "MCP_TOOL_META"):
                tools.append(mod.MCP_TOOL_META)
        except Exception as e:
            print(f"[ToolRegistry] Failed to import {mod_name}: {e}")
    return {"tools": tools}