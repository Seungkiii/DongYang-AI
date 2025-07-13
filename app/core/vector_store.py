import os
import logging
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import chromadb
from chromadb.config import Settings
import time

logger = logging.getLogger(__name__)

class OpenAIEmbeddingFunction:
    def __init__(self, openai_api_key: str, model: str = "text-embedding-ada-002"):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model=model
        )
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(input)

class VectorStore:
    def __init__(self, openai_api_key: str, collection_name: str = "insurance_docs"):
        self.openai_api_key = openai_api_key
        self.collection_name = collection_name
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path="./vector_store",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 임베딩 함수 생성
        self.embedding_function = OpenAIEmbeddingFunction(openai_api_key)
        
        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ Existing collection '{collection_name}' loaded")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ New collection '{collection_name}' created")
    
    def add_documents_batch(self, documents: List[Document], batch_size: int = 100, max_retries: int = 3):
        """배치 처리로 문서 추가"""
        total_docs = len(documents)
        logger.info(f"🔄 Adding {total_docs} documents in batches of {batch_size}")
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_docs + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")
            
            # 재시도 로직
            for attempt in range(max_retries):
                try:
                    texts = [doc.page_content for doc in batch]
                    metadatas = [doc.metadata for doc in batch]
                    ids = [f"doc_{i + j}" for j in range(len(batch))]
                    
                    self.collection.add(
                        documents=texts,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    logger.info(f"✅ Batch {batch_num} completed successfully")
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 지수 백오프
                        logger.warning(f"⚠️ Batch {batch_num} failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ Batch {batch_num} failed after {max_retries} attempts: {e}")
                        raise
            
            # API 레이트 제한 방지를 위한 짧은 대기
            if i + batch_size < total_docs:
                time.sleep(1)
        
        logger.info(f"🎉 All {total_docs} documents added successfully!")
    
    def add_documents(self, documents: List[Document]):
        """기존 방식 (호환성 유지)"""
        self.add_documents_batch(documents)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """유사도 검색"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    documents.append(Document(page_content=doc, metadata=metadata))
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """컬렉션 정보 반환"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {e}")
            return {
                "name": self.collection_name,
                "count": 0,
                "status": "error"
            } 