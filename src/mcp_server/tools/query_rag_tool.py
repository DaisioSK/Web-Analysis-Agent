# mcp_server/tools/query_rag_tool.py
from fastapi import APIRouter
from pydantic import BaseModel
from mcp_server.rag.retriever import search_documents
from mcp_server.rag.prompt import format_context, rag_prompt
from langchain_openai import ChatOpenAI

router = APIRouter()

MCP_TOOL_META = {
    "name": "query_rag",
    "description": "RAG: 使用知识库回答问题，并返回引用片段"
}

class QueryInput(BaseModel):
    question: str
    top_k: int = 3

@router.post("/query_rag")
def query_rag(input: QueryInput):
    try:
        docs = search_documents(input.question, k=input.top_k)
        context = format_context(docs)

        prompt = rag_prompt.format_messages(
            context=context,
            question=input.question
        )

        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini")
        response = llm.invoke(prompt)

        return {
            "question": input.question,
            "answer": response.content,
            "sources": [d.metadata for d in docs],
        }
    except Exception as e:
        return {"error": str(e)}