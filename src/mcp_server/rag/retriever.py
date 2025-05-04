# mcp_server/rag/retriever.py
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 设置路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = BASE_DIR / "mcp_server/rag/faiss_index"

# 嵌入模型
embedding = OpenAIEmbeddings()

# 加载本地 FAISS 向量库
def load_vectorstore():
    return FAISS.load_local(
        str(INDEX_DIR),
        embeddings=embedding,
        allow_dangerous_deserialization=True
    )

# 查询接口
def search_documents(query: str, k: int = 3) -> list[Document]:
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results


def list_all_chunks(limit=10):
    vectorstore = load_vectorstore()
    all_docs = vectorstore.docstore._dict  # 所有 chunk（id -> Document）
    print(f"Total chunks: {len(all_docs)}\n")
    for i, (doc_id, doc) in enumerate(all_docs.items()):
        print(f"--- Chunk {i+1} [{doc.metadata.get('source')}] ---")
        print(doc.page_content[:500] + "\n")
        if i + 1 >= limit:
            break


# 可选：测试用入口
if __name__ == "__main__":
    print("\n=== Checking chunks ===")
    list_all_chunks(limit=10)
    
    print("\n=== Searching for documents ===")
    query = "What are the major trends in web analytics in 2025?"
    docs = search_documents(query)
    for i, doc in enumerate(docs):
        print(f"\n=== Result {i+1} ===")
        print(doc.page_content[:300])
        print("Source:", doc.metadata.get("source"))
