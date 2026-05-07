"""
RAG模块 - 向量检索器
"""
import os
import json
from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from .loader import LegalDocLoader


class LegalRetriever:
    """法律文档检索器"""
    
    def __init__(
        self,
        user_id: str,
        docs_dir: str = None,
        collection_name: str = None
    ):
        self.user_id = user_id
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.collection_name = collection_name or f"legal_docs_{user_id}"
        self.embeddings = None
        self.vectorstore = None
    
    def set_api_key(self, api_key: str, provider: str = "openai") -> None:
        """设置API Key"""
        os.environ["OPENAI_API_KEY"] = api_key
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )
    
    def build_index(
        self,
        documents: List[Document] = None,
        docs_dir: str = None,
        regenerate: bool = False
    ) -> bool:
        """构建向量索引"""
        if documents is None:
            docs_dir = docs_dir or self.docs_dir
            if not docs_dir:
                return False
            
            loader = LegalDocLoader(docs_dir)
            documents = loader.load_directory(docs_dir)
        
        if not documents:
            return False
        
        # 创建向量存储
        persist_dir = self._get_persist_dir()
        
        if regenerate:
            self._delete_collection()
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=str(persist_dir)
        )
        
        return True
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: dict = None
    ) -> List[Document]:
        """相似度检索"""
        if not self.vectorstore:
            self._load_index()
        
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter=filter
        )
        
        return results
    
    def search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict = None
    ) -> List[tuple]:
        """带相似度分数的检索"""
        if not self.vectorstore:
            self._load_index()
        
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter
        )
        
        return results
    
    def _get_persist_dir(self) -> Path:
        """获取向量存储目录"""
        base = Path("D:/AI_agent/data/vectorstore")
        return base / self.user_id
    
    def _load_index(self) -> bool:
        """加载已有索引"""
        persist_dir = self._get_persist_dir()
        
        if not persist_dir.exists():
            return False
        
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(persist_dir)
            )
            return True
        except:
            return False
    
    def _delete_collection(self) -> None:
        """删除向量集合"""
        try:
            client = chromadb.PersistentClient(path=str(self._get_persist_dir().parent))
            client.delete_collection(name=self.collection_name)
        except:
            pass
        
        persist_dir = self._get_persist_dir()
        if persist_dir.exists():
            import shutil
            shutil.rmtree(persist_dir)
    
    def get_document_count(self) -> int:
        """获取索引文档数量"""
        if not self.vectorstore:
            self._load_index()
        
        if self.vectorstore:
            return self.vectorstore._collection.count()
        return 0