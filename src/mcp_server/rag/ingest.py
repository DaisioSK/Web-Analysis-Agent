# mcp_server/rag/ingest.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

# from dotenv import load_dotenv
# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 假设该文件在 src/mcp_server/rag/ingest.py
DATA_DIR = BASE_DIR / "docs"  # 假设 PDF 文件在 docs 目录下
INDEX_DIR = BASE_DIR / "mcp_server/rag/faiss_index"  # 假设索引文件在 mcp_server/rag/faiss_index 目录下


all_docs = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(DATA_DIR, filename)
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["filetype"] = 'pdf'  # 加入文件类型信息
            doc.metadata["source"] = filename
        all_docs.extend(docs)

print(f"Loaded {len(all_docs)} documents.")

# 文本切分器：推荐 chunk_size 500 tokens，带 50 overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
split_docs = splitter.split_documents(all_docs)
print(f"Split into {len(split_docs)} chunks.")

# 嵌入模型（OpenAI，也可以改成本地模型）
embeddings = OpenAIEmbeddings()

# 创建 FAISS 向量索引
vectorstore = FAISS.from_documents(split_docs, embeddings)
vectorstore.save_local(INDEX_DIR)
print(f"FAISS index saved to: {INDEX_DIR}")
print("总向量数：", vectorstore.index.ntotal)
print("向量维度：", vectorstore.index.d)
print("索引类型：", type(vectorstore.index))