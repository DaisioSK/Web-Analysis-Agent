# mcp_server/rag/prompt.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# 拼接检索片段为 prompt 格式的上下文字符串
def format_context(docs: list[Document]) -> str:
    context = ""
    for i, doc in enumerate(docs):
        content = doc.page_content.strip()
        source = doc.metadata.get("source", "unknown")
        context += f"[Source {i+1}: {source}]:\n{content}\n\n"
    return context.strip()

# 构造一个用于 RAG 问答的 PromptTemplate
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant for answering questions using the provided context."),
    ("human", "Use the following context to answer the question. If the answer is not found, say you don't know.\n\nContext:\n{context}\n\nQuestion: {question}")
])
