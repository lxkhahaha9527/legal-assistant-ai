"""
RAG模块 - 文档加载器
支持: txt, pdf, doc, docx
"""
import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class LegalDocLoader:
    """法律文档加载器"""
    
    SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.doc', '.docx']
    
    def __init__(self, docs_dir: str = None):
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
    
    def load_file(self, file_path: str) -> List[Document]:
        """加载单个文件"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        loader = self._get_loader(path, ext)
        docs = loader.load()
        
        # 分割文档
        if len(docs) > 1:
            return self.splitter.split_documents(docs)
        else:
            return self.splitter.split_documents(docs)
    
    def _get_loader(self, path: Path, ext: str):
        """根据扩展名获取加载器"""
        if ext == '.txt':
            return TextLoader(str(path), encoding='utf-8')
        elif ext == '.pdf':
            return PyPDFLoader(str(path))
        elif ext in ['.doc', '.docx']:
            return UnstructuredWordDocumentLoader(str(path))
        else:
            raise ValueError(f"不支持的格式: {ext}")
    
    def load_directory(self, directory: str) -> List[Document]:
        """加载目录下所有支持的文件"""
        docs = []
        dir_path = Path(directory)
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    docs.extend(self.load_file(str(file_path)))
                except Exception as e:
                    print(f"加载失败 {file_path.name}: {e}")
        
        return docs
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return self.SUPPORTED_EXTENSIONS