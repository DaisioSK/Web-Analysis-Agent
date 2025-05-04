# run_rag_demo.py
from mcp_server.rag.retriever import search_documents
from mcp_server.rag.prompt import format_context, rag_prompt
from langchain_openai import ChatOpenAI

if __name__ == "__main__":
    question = "What are the major trends in web analytics in 2025?"
    docs = search_documents(question, k=4)
    context = format_context(docs)

    print("\n===== RAG Context =====\n")
    print(context[:1000] + ("..." if len(context) > 1000 else ""))

    prompt = rag_prompt.format_messages(
        context=context,
        question=question
    )

    llm = ChatOpenAI(temperature=0.2, model_name="gpt-4")
    response = llm.invoke(prompt)

    print("\n===== Answer =====\n")
    print(response.content)

    print("\n===== Sources =====\n")
    for i, doc in enumerate(docs):
        print(f"[{i+1}]", doc.metadata.get("source"))
