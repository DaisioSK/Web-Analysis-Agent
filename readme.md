# 🧠 LangChain MCP Agent

This project is an intelligent **LangChain Agent** that integrates with a **local MCP tool server** (built with FastAPI). It can analyze webpages and UI screenshots, automatically select appropriate tools, and return **structured tracking component suggestions**.

---

## 🚀 Features

- 🔧 Auto-discovered MCP tools (via FastAPI)
- 🧠 LangChain Agent with OpenAI LLM and structured output (Pydantic)
- 🖼️ Screenshot + DOM analysis
- 📦 Outputs include: component name, bounding box, metric definition, tracking method, interactivity, etc.

---

## 🛠️ Installation

```bash
# Clone this repo
git clone https://github.com/your-username/langchain-mcp-agent.git
cd langchain-mcp-agent

# Create virtual environment
conda create -n ai_agent_env python=3.9
conda activate ai_agent_env

# Install dependencies
pip install -r requirements.txt

---

## 🖥️ Running the MCP Server

```bash
# Enter the project base directory
cd "...\langchain agent basic\langchain agent\src"

# Launch FastAPI server for MCP tools
uvicorn mcp_server.main:app --reload
python -m uvicorn mcp_server.main:app
# or 
uvicorn mcp_server.main:app --reload

# This will expose local tools at:
👉 http://localhost:8000/docs/

